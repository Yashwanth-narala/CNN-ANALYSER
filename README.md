# 🧪 Liquid Crystal CNN Analyzer

A modern web application that uses Convolutional Neural Networks (CNN) to analyze liquid crystal phase transitions from microscope images. This tool is designed for materials science research, specifically for detecting phase transitions in liquid crystal samples at different temperatures.

## 🎯 Features

- **Live Camera Analysis**: Real-time microscope camera feed with instant capture and analysis
- **File Upload Analysis**: Upload and analyze microscope images from your device
- **Deep Learning Analysis**: Uses pre-trained VGG16 CNN for feature extraction
- **Multiple Metrics**: Computes 6 different metrics (Mean, Std Deviation, RMS, Entropy, Contrast, Energy)
- **Interactive Visualization**: Real-time graphs with transition markers
- **Report Generation**: Exports results as CSV and PDF reports
- **Modern UI**: Clean, responsive interface built with React Router and Tailwind CSS

## 🏗️ Architecture

- **Frontend**: React.js with React Router for navigation
- **Backend**: Flask API with CNN analysis
- **AI Model**: Pre-trained VGG16 CNN for feature extraction
- **Data Processing**: PCA, curvature analysis, and statistical metrics

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## 🚀 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## 📸 Usage

### Home Page (`/`)
- Choose between "Live Analysis" or "File Analysis"
- Professional UI with clear navigation options

### Live Analysis (`/live-analysis`)
1. **Camera Access**: Grant camera permissions when prompted
2. **Temperature Input**: Enter the current temperature of your sample
3. **Capture & Analyze**: Click to capture the current frame and analyze
4. **View Results**: See real-time analysis results with metrics and graphs

### File Analysis (`/file-analysis`)
1. **Upload Image**: Select a microscope image file (JPG, JPEG, PNG)
2. **Temperature Input**: Enter the temperature at which the image was taken
3. **Analyze**: Click to process the image and get results
4. **Download Reports**: Export results as CSV or PDF

## 🔬 Sample Data

The project includes sample images in `backend/backend/static/uploads/`:
- `IMG_1412 118.2C isotropic.JPG` (118.2°C)
- `IMG_1413 117.3C isotropic to nematic droplets.JPG` (117.3°C)  
- `IMG_1414 117.0C.JPG` (117.0°C)

## 📊 Metrics Explained

- **Mean**: Average feature values from CNN
- **Std Deviation**: Variability in feature values
- **RMS**: Root Mean Square of features
- **Entropy**: Information content measure
- **Contrast**: Feature contrast between image regions
- **Energy**: Signal energy content

## 🔍 Phase Transitions

The system detects three main liquid crystal phase transitions:
1. **Isotropic → Nematic Droplets**
2. **Fully Nematic Phase**
3. **Nematic → Solid**

## 🛠️ Technical Details

### Frontend Components
- **HomePage**: Landing page with navigation options
- **LiveAnalysisPage**: Camera feed and real-time analysis
- **FileAnalysisPage**: File upload and analysis interface
- **MetricGraph**: Interactive data visualization component

### Backend API Endpoints
- `POST /api/analyze`: File upload analysis
- `POST /api/live-analyze`: Live camera analysis
- `GET /download/csv`: Download CSV reports
- `GET /download/pdf`: Download PDF reports
- `GET /download/live-csv`: Download live analysis CSV
- `GET /download/live-pdf`: Download live analysis PDF

## 🐛 Troubleshooting

1. **Camera Access**: Ensure camera permissions are granted in your browser
2. **Backend Connection**: Verify Flask server is running on port 5000
3. **Image Processing**: Check that images contain valid data
4. **Dependency Issues**: Verify all Python and Node.js packages are installed

## 📝 License

This project is designed for research purposes. Please ensure proper attribution when using this tool in academic or commercial applications.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests. 