import os
import re
import numpy as np
import cv2
from collections import Counter
from typing import Dict
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore
from sklearn.decomposition import PCA
from scipy.stats import entropy
from optical_parameters import calculate_optical_parameters_batch_ultra_optimized as calculate_optical_parameters_batch
from temperature_interpolation import extract_temperature_from_filename, interpolate_temperatures

# Load pretrained VGG16 model without top
model = VGG16(weights='imagenet', include_top=False, input_shape=(128, 128, 3))

def extract_temperature(filename):
    # Use the new temperature extraction function
    temp = extract_temperature_from_filename(filename)
    if temp is not None:
        print(f"Extracted temperature from {filename}: {temp}°C")  # Debug log
        return temp
    print(f"No temperature found in filename: {filename}")  # Debug log
    return None

def normalize(arr):
    arr = np.array(arr)
    return (arr - arr.min()) / (arr.max() - arr.min() + 1e-8)

def detect_transitions(metrics_data, sorted_temps, top_n=5):
    all_detected = []
    for label, values in metrics_data:
        dy = np.gradient(values)
        ddy = np.gradient(dy)
        curvature = np.abs(ddy)
        peak_indices = np.argsort(curvature)[-top_n:]
        detected_temps = [round(sorted_temps[i], 1) for i in peak_indices]
        all_detected.extend(detected_temps)

    temp_counts = Counter(all_detected)
    top_transitions = [t for t, _ in temp_counts.most_common(3)]
    top_transitions.sort(reverse=True)

    phase_labels = [
        "Isotropic → Nematic Droplets",
        "Fully Nematic Phase",
        "Nematic → Solid"
    ]
    return {label: temp for label, temp in zip(phase_labels, top_transitions)}

def run_cnn_analysis(image_folder):
    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])

    cnn_features, temps, filenames = [], [], []

    # Pre-allocate arrays for better performance
    n_images = len(image_files)
    if n_images == 0:
        raise ValueError("No valid images found in folder.")
    
    # Process images in batches for better performance
    batch_size = min(4, n_images)  # Process 4 images at a time or less
    
    for i in range(0, n_images, batch_size):
        batch_files = image_files[i:i+batch_size]
        batch_features = []
        batch_temps = []
        batch_filenames = []
        
        for filename in batch_files:
            temp = extract_temperature(filename)
            # For single image analysis, use a default temperature if none found
            if temp is None:
                temp = 25.0  # Default room temperature

            filepath = os.path.join(image_folder, filename)
            img = cv2.imread(filepath)
            if img is None:
                continue

            # Optimize image processing
            img = cv2.resize(img, (128, 128))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_array = img_to_array(img)
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            batch_features.append(img_array)
            batch_temps.append(temp)
            batch_filenames.append(filename)
        
        if batch_features:
            # Process batch through CNN
            batch_array = np.vstack(batch_features)
            features = model.predict(batch_array, verbose=0)
            
            for feat, temp, filename in zip(features, batch_temps, batch_filenames):
                cnn_features.append(feat.flatten())
                temps.append(temp)
                filenames.append(filename)

    if len(cnn_features) < 1:
        raise ValueError("At least 1 valid image is required for analysis.")

    features_array = np.array(cnn_features)
    temps_array = np.array(temps)

    pca = PCA(n_components=1)
    reduced = pca.fit_transform(features_array).flatten()

    sorted_idx = np.argsort(temps_array)
    sorted_temps = temps_array[sorted_idx]
    sorted_features = features_array[sorted_idx]
    sorted_filenames = [filenames[i] for i in sorted_idx]

    # Optimized Metric Computation
    mean_vals, std_vals, rms_vals, entropy_vals, contrast_vals, energy_vals = [], [], [], [], [], []

    for feat in sorted_features:
        feat_norm = normalize(feat)
        mean_vals.append(np.mean(feat_norm))
        std_vals.append(np.std(feat_norm))
        rms_vals.append(np.sqrt(np.mean(feat_norm**2)))

        # Optimize histogram calculation
        hist, _ = np.histogram(feat_norm, bins=64, range=(0, 1), density=True)
        hist += 1e-8
        entropy_vals.append(entropy(hist))

        # Optimize contrast calculation
        mid = len(feat_norm) // 2
        contrast_vals.append(np.abs(np.std(feat_norm[:mid]) - np.std(feat_norm[mid:])))
        energy_vals.append(np.sum(feat_norm**2))

    # Calculate optical parameters for all images (optimized)
    transmittance_vals, absorption_coeff_vals, refractive_index_vals, birefringence_vals = calculate_optical_parameters_batch(image_folder)
    
    # Sort optical parameters according to the same temperature ordering
    sorted_transmittance = [transmittance_vals[i] for i in sorted_idx]
    sorted_absorption_coeff = [absorption_coeff_vals[i] for i in sorted_idx]
    sorted_refractive_index = [refractive_index_vals[i] for i in sorted_idx]
    sorted_birefringence = [birefringence_vals[i] for i in sorted_idx]

    metric_data = {
        "Temperature": [float(t) for t in sorted_temps.tolist()],
        "Filename": sorted_filenames,
        "Mean": [float(v) for v in mean_vals],
        "Std Deviation": [float(v) for v in std_vals],
        "RMS": [float(v) for v in rms_vals],
        "Entropy": [float(v) for v in entropy_vals],
        "Contrast": [float(v) for v in contrast_vals],
        "Energy": [float(v) for v in energy_vals],
        "Transmittance": [float(v) for v in sorted_transmittance],
        "Absorption_Coefficient": [float(v) for v in sorted_absorption_coeff],
        "Refractive_Index": [float(v) for v in sorted_refractive_index],
        "Birefringence": [float(v) for v in sorted_birefringence]
    }

    metrics_for_transition = [
        ("Mean", mean_vals),
        ("Std Deviation", std_vals),
        ("RMS", rms_vals),
        ("Entropy", entropy_vals),
        ("Contrast", contrast_vals),
        ("Energy", energy_vals),
        ("Transmittance", sorted_transmittance),
        ("Absorption_Coefficient", sorted_absorption_coeff),
        ("Refractive_Index", sorted_refractive_index),
        ("Birefringence", sorted_birefringence)
    ]
    # Only detect transitions if we have multiple images
    if len(sorted_temps) >= 3:
        transitions = detect_transitions(metrics_for_transition, sorted_temps)
        # Convert transition temperatures to float for JSON serialization
        transitions = {label: float(temp) for label, temp in transitions.items()}
    else:
        # For single image analysis, no transitions to detect
        transitions = {}

    return {
        "metric_data": metric_data,
        "transitions": transitions
    }

def run_cnn_analysis_with_temperature_range(image_folder: str, start_temp: float, end_temp: float) -> Dict:
    """
    Run CNN analysis with interpolated temperature range.
    
    Args:
        image_folder: Folder containing images
        start_temp: Starting temperature in Celsius
        end_temp: Ending temperature in Celsius
    
    Returns:
        Analysis result with interpolated temperatures
    """
    # Get all image files
    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    
    if len(image_files) < 1:
        raise ValueError("At least 1 valid image is required for analysis.")
    
    # Interpolate temperatures for all images
    temperatures = interpolate_temperatures(start_temp, end_temp, len(image_files))
    
    # Rename files with temperature information if they don't already have it
    renamed_files = []
    for idx, (filename, temp) in enumerate(zip(image_files, temperatures)):
        # Check if filename already has temperature info
        existing_temp = extract_temperature_from_filename(filename)
        
        if existing_temp is None:
            # Rename file to include temperature
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{temp:.1f}C{ext}"
            old_path = os.path.join(image_folder, filename)
            new_path = os.path.join(image_folder, new_filename)
            
            try:
                os.rename(old_path, new_path)
                renamed_files.append(new_path)
            except Exception as e:
                print(f"Warning: Could not rename {filename}: {str(e)}")
                renamed_files.append(old_path)
        else:
            renamed_files.append(os.path.join(image_folder, filename))
    
    # Run the standard analysis (which will now use the temperature-annotated filenames)
    return run_cnn_analysis(image_folder)
