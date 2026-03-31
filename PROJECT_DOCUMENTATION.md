# Liquid Crystal CNN WebApp - Project Documentation

## 1) Project Overview

This project is a full-stack web application for liquid crystal phase analysis from microscope images and camera/video input. It combines deep learning feature extraction (VGG16), optical parameter estimation, transition detection logic, and downloadable reporting (CSV/PDF).

Primary goal:
- Analyze image or video-derived frames across temperature progression.
- Compute scientific metrics and detect likely phase transition points.
- Provide a researcher-friendly dashboard for visualization and export.

## 2) What Has Been Implemented (Work Done So Far)

### Core Analysis Pipeline
- CNN feature extraction using pre-trained VGG16 (`include_top=False`) on resized images.
- Dimensionality reduction with PCA.
- Metric computation:
  - Mean
  - Std Deviation
  - RMS
  - Entropy
  - Contrast
  - Energy
- Optical parameter integration:
  - Transmittance
  - Absorption Coefficient
  - Refractive Index
  - Birefringence
- Transition detection using curvature peaks across multiple metrics.

### Temperature Range and Interpolation
- Implemented linear interpolation between `start_temp` and `end_temp`.
- Supports:
  - Batch image analysis with interpolated temperatures.
  - Live video-frame capture analysis with interpolated temperatures.
  - Video file upload analysis with interpolated temperatures.
- Backward compatibility maintained for filename-based temperature extraction.

### Backend API and Reports
- Flask API endpoints for image, live camera frame, and video processing.
- CSV and PDF report generation for all analysis modes.
- Separate download endpoints for regular, live, and video analysis outputs.

### Frontend UX
- Multi-page React app with routing:
  - Home
  - File Analysis
  - Live Analysis (camera + mode selection image/video)
  - Results Dashboard
- Graph-based metric visualization using Recharts.
- Summary cards, transitions view, and report download buttons.
- Tailwind CSS styling for modern UI.

## 3) Tech Stack

### Frontend
- React 18
- React Router DOM v6
- Recharts
- Tailwind CSS
- PostCSS + Autoprefixer
- React Scripts (CRA toolchain)

### Backend
- Python
- Flask
- Flask-CORS
- TensorFlow / Keras (VGG16)
- OpenCV
- NumPy
- SciPy
- scikit-learn (PCA)
- pandas
- matplotlib
- Pillow

## 4) Architecture

### High-Level Flow
1. User uploads files / captures frames from camera / uploads video.
2. Frontend sends multipart form data to Flask endpoints.
3. Backend stores temporary files in `backend/static/uploads`.
4. Analysis pipeline computes CNN + optical + derived metrics.
5. Transition detection estimates key phase transition temperatures.
6. Backend stores reports in `backend/static/output`.
7. Frontend receives JSON metrics and renders interactive charts.
8. User downloads CSV/PDF reports via provided URLs.

### Key Backend Modules
- `backend/app.py`  
  API routes, file handling, orchestration, response formatting.
- `backend/analyzer.py`  
  CNN inference, feature processing, metrics, transitions.
- `backend/temperature_interpolation.py`  
  Temperature interpolation, validation, extraction, video frame handling.
- `backend/optical_parameters.py`  
  Fast optical parameter calculations and batch utilities.
- `backend/report_generator.py`  
  CSV/PDF report output and plotting.

### Key Frontend Modules
- `frontend/src/pages/HomePage.js`
- `frontend/src/pages/FileAnalysisPage.js`
- `frontend/src/pages/LiveAnalysisPage.js`
- `frontend/src/pages/ResultsPage.js`
- `frontend/src/components/MetricGraph.js`

## 5) API Endpoint Reference

- `GET /api/test`
- `POST /api/analyze`
  - Inputs: `images[]`, optional `start_temp`, `end_temp`
- `POST /api/live-analyze`
  - Input: `image`
- `POST /api/live-analyze-video`
  - Inputs: `images[]`, optional `start_temp`, `end_temp`, optional `frame_count`, `frame_interval`
- `POST /api/analyze-video`
  - Inputs: `video`, required `start_temp`, `end_temp`, optional `frame_count`, `frame_interval`
- `POST /analyze` (legacy compatibility)

Downloads:t
- `GET /download/csv`
- `GET /download/pdf`
- `GET /download/live-csv`
- `GET /download/live-pdf`
- `GET /download/video-csv`
- `GET /download/video-pdf`

## 6) Data Returned to Frontend

Main response fields:
- `metrics`: dictionary containing temperature series, filename series, and all metric arrays.
- `transitions`: map of phase label to detected transition temperature.
- `csv_url`, `pdf_url`: direct report download links.
- Additional fields for video mode: frame count and temperature range metadata.

## 7) Live Analysis of Current Codebase (Current State)

### Strengths
- End-to-end product is functional: input -> analysis -> visualization -> report.
- Temperature interpolation and video analysis support are integrated.
- Good modular separation in backend analytical logic.
- Includes both DL-derived and physically motivated optical indicators.
- Reporting workflow (CSV/PDF) is complete.

### Gaps / Risks Identified
- README is partially outdated vs implementation:
  - Mentions only 6 metrics, but backend currently produces 10 non-temperature metrics.
  - Video endpoints/features are under-documented in README.
- Frontend still has debugging logs in production UI paths.
- Frontend `FileAnalysisPage` currently does not expose temperature-range controls although backend supports them.
- In `LiveAnalysisPage`, analyze button disable condition uses `!temperature` globally; this can block some temperature-range flows unintentionally.
- No formal automated tests found for frontend/backend behavior.
- Running Flask in `debug=True` in main entrypoint is not production-safe.
- Upload/output folders are shared and overwritten per request (single-user/dev friendly, but risky for concurrent multi-user deployment).

### Performance Notes
- Existing optimizations include batch CNN prediction and simplified optical calculations.
- Suitable for small/medium data batches; large-scale or real-time production can still benefit from:
  - GPU-enabled deployment tuning
  - background jobs/queue
  - caching and async report generation

## 8) Suggested Next Improvements

1. Update `README.md` to fully match current features and endpoints.
2. Add frontend temperature-range controls in file-analysis UI (or remove stale references).
3. Fix analyze-button enable logic in live page for range mode.
4. Add validation and tests:
   - Unit tests for interpolation and transition detection
   - API integration tests for each endpoint
   - Frontend E2E happy-path checks
5. Add production hardening:
   - environment-based config
   - remove debug mode in production
   - request isolation for uploads/results
6. Add model/runtime observability:
   - latency metrics
   - error tracing
   - per-endpoint timing.

## 9) Run Instructions (Current)

Backend:
- `cd backend`
- `python -m venv venv`
- activate venv
- `pip install -r requirements.txt`
- `python app.py`

Frontend:
- `cd frontend`
- `npm install`
- `npm start`

Default local URLs:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

## 10) Conclusion

This project is a strong research-oriented analysis system with implemented CNN + optical metric fusion, temperature interpolation support, and practical report generation. It is feature-rich for prototyping and internal research workflows. Main next step is documentation/test/production alignment so behavior and docs remain fully consistent.
