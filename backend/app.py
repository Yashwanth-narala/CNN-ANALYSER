from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import shutil
from typing import List

from analyzer import run_cnn_analysis, run_cnn_analysis_with_temperature_range
from report_generator import generate_csv, generate_pdf
from temperature_interpolation import validate_temperature_range

# Use absolute paths so deployments work from any working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DEFAULT_OUTPUT_FOLDER = os.path.join(BASE_DIR, "static", "output")

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", DEFAULT_UPLOAD_FOLDER)
OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", DEFAULT_OUTPUT_FOLDER)

# Public base URL for building download links. If not provided, Flask request.host_url is used.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")

cors_origins_env = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).strip()
cors_origins: List[str] = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

def build_public_url() -> str:
    if PUBLIC_BASE_URL:
        return PUBLIC_BASE_URL
    return request.host_url.rstrip("/")

# Ensure folders exist for production servers (gunicorn/uwsgi don't run __main__).
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
# NOTE: keep CORS limited to your frontend origins in production.
CORS(
    app,
    origins=cors_origins,
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
)
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", "50")) * 1024 * 1024  # MB

@app.route('/api/test', methods=['GET', 'OPTIONS'])
def test_endpoint():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({"message": "Preflight OK"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response
    return jsonify({"message": "Backend is running!", "status": "success"})

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_images():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({"message": "Preflight OK"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response
    
    try:
        if 'images' not in request.files:
            return jsonify({"error": "No images uploaded"}), 400

        # Get temperature range parameters from form data
        start_temp = request.form.get('start_temp')
        end_temp = request.form.get('end_temp')
        
        # Clear previous uploads
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        print(f"Upload folder created: {UPLOAD_FOLDER}")
    except Exception as e:
        print(f"Error in setup: {str(e)}")
        return jsonify({"error": f"Setup failed: {str(e)}"}), 500

    # Save uploaded images
    files = request.files.getlist('images')
    saved_files = []
    
    for idx, f in enumerate(files):
        try:
            # Sanitize filename to remove path separators and special characters
            import re
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', f.filename)
            safe_filename = safe_filename.replace('/', '_').replace('\\', '_')
            
            # If filename is still problematic, use a generic name
            if not safe_filename or safe_filename.startswith('.'):
                safe_filename = f"image_{idx+1}.jpg"
            
            file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
            f.save(file_path)
            saved_files.append(file_path)
            print(f"Saved file: {file_path}")
        except Exception as e:
            print(f"Error saving file {f.filename}: {str(e)}")
            return jsonify({"error": f"Failed to save file {f.filename}: {str(e)}"}), 500
    
    if not saved_files:
        return jsonify({"error": "No files were successfully saved"}), 400

    try:
        # Check if temperature range parameters are provided
        if start_temp is not None and end_temp is not None:
            try:
                start_temp = float(start_temp)
                end_temp = float(end_temp)
                
                # Validate temperature range
                if not validate_temperature_range(start_temp, end_temp):
                    return jsonify({"error": "Invalid temperature range"}), 400
                
                print(f"Using temperature range: {start_temp}°C to {end_temp}°C")
                # Run analysis with temperature interpolation
                analysis_result = run_cnn_analysis_with_temperature_range(UPLOAD_FOLDER, start_temp, end_temp)
            except ValueError as e:
                return jsonify({"error": f"Invalid temperature values: {str(e)}"}), 400
        else:
            # Run standard analysis (extract temperatures from filenames)
            analysis_result = run_cnn_analysis(UPLOAD_FOLDER)
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

    # Save reports
    csv_path = os.path.join(OUTPUT_FOLDER, "results.csv")
    pdf_path = os.path.join(OUTPUT_FOLDER, "results.pdf")
    generate_csv(csv_path, analysis_result)
    generate_pdf(pdf_path, analysis_result)

    return jsonify({
        "metrics": analysis_result["metric_data"],
        "transitions": analysis_result["transitions"],
        "csv_url": build_public_url() + "/download/csv",
        "pdf_url": build_public_url() + "/download/pdf"
    })

@app.route('/api/live-analyze', methods=['POST'])
def live_analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    # Clear previous uploads
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save uploaded image
    image_file = request.files['image']
    # Sanitize filename to remove path separators and special characters
    import re
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', image_file.filename)
    safe_filename = safe_filename.replace('/', '_').replace('\\', '_')
    
    # If filename is still problematic, use a generic name
    if not safe_filename or safe_filename.startswith('.'):
        safe_filename = "live_image.jpg"
    
    image_file.save(os.path.join(UPLOAD_FOLDER, safe_filename))

    try:
        # Run analysis
        analysis_result = run_cnn_analysis(UPLOAD_FOLDER)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

    # Save reports
    csv_path = os.path.join(OUTPUT_FOLDER, "live_results.csv")
    pdf_path = os.path.join(OUTPUT_FOLDER, "live_results.pdf")
    generate_csv(csv_path, analysis_result)
    generate_pdf(pdf_path, analysis_result)

    return jsonify({
        "metrics": analysis_result["metric_data"],
        "transitions": analysis_result["transitions"],
        "csv_url": build_public_url() + "/download/live-csv",
        "pdf_url": build_public_url() + "/download/live-pdf"
    })

@app.route('/api/live-analyze-video', methods=['POST'])
def live_analyze_video():
    if 'images' not in request.files:
        return jsonify({"error": "No images uploaded"}), 400

    # Get temperature range parameters from form data
    start_temp = request.form.get('start_temp')
    end_temp = request.form.get('end_temp')
    frame_count = request.form.get('frame_count')
    frame_interval = request.form.get('frame_interval')

    # Clear previous uploads
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save uploaded frames
    files = request.files.getlist('images')
    saved_files = []
    
    for idx, f in enumerate(files):
        try:
            # Sanitize filename
            safe_filename = f"frame_{idx+1:03d}.jpg"
            file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
            f.save(file_path)
            saved_files.append(file_path)
        except Exception as e:
            print(f"Error saving frame {idx+1}: {str(e)}")
            continue

    if not saved_files:
        return jsonify({"error": "No frames were successfully saved"}), 400

    try:
        # Check if temperature range parameters are provided
        if start_temp is not None and end_temp is not None:
            try:
                start_temp = float(start_temp)
                end_temp = float(end_temp)
                
                # Validate temperature range
                if not validate_temperature_range(start_temp, end_temp):
                    return jsonify({"error": "Invalid temperature range"}), 400
                
                print(f"Using temperature range: {start_temp}°C to {end_temp}°C for {len(saved_files)} frames")
                # Run analysis with temperature interpolation
                analysis_result = run_cnn_analysis_with_temperature_range(UPLOAD_FOLDER, start_temp, end_temp)
            except ValueError as e:
                return jsonify({"error": f"Invalid temperature values: {str(e)}"}), 400
        else:
            # Run standard analysis (extract temperatures from filenames)
            analysis_result = run_cnn_analysis(UPLOAD_FOLDER)
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

    # Save reports
    csv_path = os.path.join(OUTPUT_FOLDER, "live_results.csv")
    pdf_path = os.path.join(OUTPUT_FOLDER, "live_results.pdf")
    generate_csv(csv_path, analysis_result)
    generate_pdf(pdf_path, analysis_result)

    return jsonify({
        "metrics": analysis_result["metric_data"],
        "transitions": analysis_result["transitions"],
        "csv_url": build_public_url() + "/download/live-csv",
        "pdf_url": build_public_url() + "/download/live-pdf"
    })

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    """Analyze video file with temperature range interpolation."""
    if 'video' not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    # Get temperature range parameters from form data
    start_temp = request.form.get('start_temp')
    end_temp = request.form.get('end_temp')
    frame_count = request.form.get('frame_count')
    frame_interval = request.form.get('frame_interval')

    if not start_temp or not end_temp:
        return jsonify({"error": "start_temp and end_temp are required"}), 400

    try:
        start_temp = float(start_temp)
        end_temp = float(end_temp)
        
        # Validate temperature range
        if not validate_temperature_range(start_temp, end_temp):
            return jsonify({"error": "Invalid temperature range"}), 400
        
        # Parse optional parameters
        frame_count = int(frame_count) if frame_count else None
        frame_interval = int(frame_interval) if frame_interval else None
        
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter values: {str(e)}"}), 400

    # Clear previous uploads
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save uploaded video
    video_file = request.files['video']
    video_path = os.path.join(UPLOAD_FOLDER, "uploaded_video.mp4")
    video_file.save(video_path)

    try:
        # Import video processing functions
        from temperature_interpolation import (
            process_video_with_temperature_range,
            save_frames_with_temperatures
        )
        
        # Extract frames with temperature interpolation
        frames, temperatures = process_video_with_temperature_range(
            video_path, start_temp, end_temp, frame_count, frame_interval
        )
        
        # Save frames with temperature information
        saved_files = save_frames_with_temperatures(frames, temperatures, UPLOAD_FOLDER)
        
        print(f"Extracted {len(frames)} frames with temperature range {start_temp}°C to {end_temp}°C")
        
        # Run analysis
        analysis_result = run_cnn_analysis(UPLOAD_FOLDER)
        
    except Exception as e:
        return jsonify({"error": f"Video processing failed: {str(e)}"}), 500

    # Save reports
    csv_path = os.path.join(OUTPUT_FOLDER, "video_results.csv")
    pdf_path = os.path.join(OUTPUT_FOLDER, "video_results.pdf")
    generate_csv(csv_path, analysis_result)
    generate_pdf(pdf_path, analysis_result)

    return jsonify({
        "metrics": analysis_result["metric_data"],
        "transitions": analysis_result["transitions"],
        "frame_count": len(frames),
        "temperature_range": f"{start_temp}°C to {end_temp}°C",
        "csv_url": build_public_url() + "/download/video-csv",
        "pdf_url": build_public_url() + "/download/video-pdf"
    })

# Keep the old endpoint for backward compatibility
@app.route('/analyze', methods=['POST'])
def analyze_images_legacy():
    return analyze_images()

@app.route('/download/csv', methods=['GET'])
def download_csv():
    path = os.path.join(OUTPUT_FOLDER, "results.csv")
    if not os.path.exists(path):
        return jsonify({"error": "CSV not found"}), 404
    return send_file(path, as_attachment=True, download_name="liquid_crystal_analysis.csv")

@app.route('/download/pdf', methods=['GET'])
def download_pdf():
    path = os.path.join(OUTPUT_FOLDER, "results.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "PDF not found"}), 404
    return send_file(path, as_attachment=True, download_name="liquid_crystal_analysis.pdf")

@app.route('/download/live-csv', methods=['GET'])
def download_live_csv():
    path = os.path.join(OUTPUT_FOLDER, "live_results.csv")
    if not os.path.exists(path):
        return jsonify({"error": "Live CSV not found"}), 404
    return send_file(path, as_attachment=True, download_name="live_liquid_crystal_analysis.csv")

@app.route('/download/live-pdf', methods=['GET'])
def download_live_pdf():
    path = os.path.join(OUTPUT_FOLDER, "live_results.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "Live PDF not found"}), 404
    return send_file(path, as_attachment=True, download_name="live_liquid_crystal_analysis.pdf")

@app.route('/download/video-csv', methods=['GET'])
def download_video_csv():
    path = os.path.join(OUTPUT_FOLDER, "video_results.csv")
    if not os.path.exists(path):
        return jsonify({"error": "Video CSV not found"}), 404
    return send_file(path, as_attachment=True, download_name="video_liquid_crystal_analysis.csv")

@app.route('/download/video-pdf', methods=['GET'])
def download_video_pdf():
    path = os.path.join(OUTPUT_FOLDER, "video_results.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "Video PDF not found"}), 404
    return send_file(path, as_attachment=True, download_name="video_liquid_crystal_analysis.pdf")

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug, host="0.0.0.0", port=port)
