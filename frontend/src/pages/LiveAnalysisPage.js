import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function LiveAnalysisPage() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [temperature, setTemperature] = useState("");
  const [startTemp, setStartTemp] = useState("");
  const [endTemp, setEndTemp] = useState("");
  const [useTemperatureRange, setUseTemperatureRange] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [cameras, setCameras] = useState([]);
  const [selectedCameraId, setSelectedCameraId] = useState("");
  const [mode, setMode] = useState("image"); // "image" or "video"
  const [videoDuration, setVideoDuration] = useState(5); // seconds
  const [frameInterval, setFrameInterval] = useState(0.5); // seconds

  // Fetch available cameras on mount
  useEffect(() => {
    async function fetchCameras() {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
          setError("Camera API not supported in this browser.");
          setCameras([]);
          return;
        }
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === "videoinput");
        setCameras(videoDevices);
        if (videoDevices.length === 0) {
          setError("No cameras found. Please connect a camera and refresh.");
        } else {
          setError("");
          setSelectedCameraId(videoDevices[0].deviceId);
        }
      } catch (err) {
        setError("Unable to list cameras. Please check permissions.");
        setCameras([]);
      }
    }
    fetchCameras();
  }, []);

  // Start camera when selectedCameraId changes
  useEffect(() => {
    async function startSelectedCamera() {
      if (!selectedCameraId) return;
      // Stop previous stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      try {
        await startCamera(selectedCameraId);
      } catch (err) {
        setError("Failed to start camera. Please check permissions or try another device.");
        setIsCameraActive(false);
        console.error("Camera start error:", err);
      }
    }
    startSelectedCamera();
    // eslint-disable-next-line
  }, [selectedCameraId]);

  const startCamera = async (deviceId) => {
    try {
      setIsCameraActive(false);
      setError("");
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Camera API not supported in this browser.");
        return;
      }
      const constraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          deviceId: deviceId ? { exact: deviceId } : undefined,
        }
      };
      console.log("Requesting camera with constraints:", constraints);
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          setIsCameraActive(true);
          setError("");
          console.log("Camera stream started successfully.");
        };
      } else {
        setError("Video element not available.");
        setIsCameraActive(false);
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError("Camera permission denied. Please allow camera access in your browser settings.");
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError("No camera device found. Please connect a camera and refresh.");
      } else {
        setError("Unable to access camera. Please check camera permissions and device availability.");
      }
      setIsCameraActive(false);
    }
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to blob
    return new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/jpeg', 0.9);
    });
  };

  const handleAnalyze = async () => {
    if (!isCameraActive) {
      setError("Camera is not active. Please check camera permissions.");
      return;
    }

    // Validate temperature input
    if (useTemperatureRange) {
      if (!startTemp || !endTemp) {
        setError("Please enter both start and end temperatures.");
        return;
      }
      
      const start = parseFloat(startTemp);
      const end = parseFloat(endTemp);
      
      if (isNaN(start) || isNaN(end)) {
        setError("Please enter valid numbers for temperatures.");
        return;
      }
      
      if (start < -273.15 || end < -273.15) {
        setError("Temperature cannot be below absolute zero (-273.15°C).");
        return;
      }
      
      if (start > 1000 || end > 1000) {
        setError("Temperature cannot exceed 1000°C.");
        return;
      }
    } else {
      if (!temperature || isNaN(temperature)) {
        setError("Please enter a valid temperature value.");
        return;
      }
    }

    setIsAnalyzing(true);
    setError("");

    try {
      if (mode === "image") {
        // Capture single frame
        const imageBlob = await captureFrame();
        if (!imageBlob) throw new Error("Failed to capture image from camera");
        const formData = new FormData();
        formData.append('image', imageBlob, 'live_capture.jpg');
        
        if (useTemperatureRange) {
          formData.append('start_temp', startTemp);
          formData.append('end_temp', endTemp);
        } else {
          formData.append('temperature', temperature);
        }
        
        const response = await fetch('http://localhost:5000/api/live-analyze', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Analysis failed');
        navigate('/results', { state: { analysisResults: data, analysisType: "Live Analysis" } });
      } else if (mode === "video") {
        // Capture multiple frames
        const totalFrames = Math.floor(videoDuration / frameInterval);
        const frameBlobs = [];
        for (let i = 0; i < totalFrames; i++) {
          // eslint-disable-next-line no-await-in-loop
          const blob = await captureFrame();
          if (blob) frameBlobs.push(blob);
          // eslint-disable-next-line no-await-in-loop
          await new Promise(res => setTimeout(res, frameInterval * 1000));
        }
        if (frameBlobs.length === 0) throw new Error("No frames captured from video");
        const formData = new FormData();
        frameBlobs.forEach((blob, idx) => {
          formData.append('images', blob, `frame_${idx + 1}.jpg`);
        });
        
        if (useTemperatureRange) {
          formData.append('start_temp', startTemp);
          formData.append('end_temp', endTemp);
        } else {
          formData.append('temperature', temperature);
        }
        
        const response = await fetch('http://localhost:5000/api/live-analyze-video', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Video analysis failed');
        navigate('/results', { state: { analysisResults: data, analysisType: "Live Video Analysis" } });
      }
    } catch (err) {
      console.error("Analysis error:", err);
      setError(err.message || "Failed to analyze. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };



  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">📹 Live Analysis</h1>
            <p className="text-gray-600 mt-2">Real-time camera feed analysis</p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </button>
        </div>

        {/* Camera selection dropdown */}
        <div className="mb-4 flex flex-col items-center">
          <label htmlFor="camera-select" className="mb-2 font-semibold">Select Camera:</label>
          <select
            id="camera-select"
            value={selectedCameraId}
            onChange={e => setSelectedCameraId(e.target.value)}
            className="border rounded px-3 py-2"
          >
            {cameras.map((camera, idx) => (
              <option key={camera.deviceId} value={camera.deviceId}>
                {camera.label || `Camera ${idx + 1}`}
              </option>
            ))}
          </select>
        </div>

        {/* Mode toggle */}
        <div className="mb-4 flex flex-col items-center">
          <label className="mb-2 font-semibold">Analysis Mode:</label>
          <div className="flex gap-4">
            <button
              className={`px-4 py-2 rounded ${mode === 'image' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800'}`}
              onClick={() => setMode('image')}
              disabled={isAnalyzing}
            >
              Image
            </button>
            <button
              className={`px-4 py-2 rounded ${mode === 'video' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800'}`}
              onClick={() => setMode('video')}
              disabled={isAnalyzing}
            >
              Video
            </button>
          </div>
        </div>

        {/* Video settings if mode is video */}
        {mode === 'video' && (
          <div className="mb-4 flex flex-col items-center">
            <label className="mb-1">Video Duration (seconds):</label>
            <input
              type="number"
              min={1}
              max={30}
              value={videoDuration}
              onChange={e => setVideoDuration(Number(e.target.value))}
              className="border rounded px-3 py-1 mb-2"
              disabled={isAnalyzing}
            />
            <label className="mb-1">Frame Interval (seconds):</label>
            <input
              type="number"
              min={0.1}
              max={2}
              step={0.1}
              value={frameInterval}
              onChange={e => setFrameInterval(Number(e.target.value))}
              className="border rounded px-3 py-1"
              disabled={isAnalyzing}
            />
          </div>
        )}

        <div className="max-w-4xl mx-auto">
          {/* Camera Feed Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Camera Feed</h2>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            <div className="relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-64 bg-gray-900 rounded-lg object-cover"
              />
              <canvas
                ref={canvasRef}
                className="hidden"
              />
              
              {!isCameraActive && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 rounded-lg">
                  <div className="text-center text-white">
                    <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <p>Camera not available</p>
                  </div>
                </div>
              )}
            </div>

            {/* Temperature Input */}
            <div className="mt-4">
              <div className="flex items-center justify-center mb-3">
                <input
                  type="checkbox"
                  id="useTemperatureRange"
                  checked={useTemperatureRange}
                  onChange={(e) => setUseTemperatureRange(e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="useTemperatureRange" className="text-sm font-medium text-gray-700">
                  Use Temperature Range (for video analysis)
                </label>
              </div>
              
              {useTemperatureRange ? (
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Start Temperature (°C)
                    </label>
                    <input
                      type="number"
                      value={startTemp}
                      onChange={(e) => setStartTemp(e.target.value)}
                      placeholder="80"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      step="0.1"
                      min="-273.15"
                      max="1000"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      End Temperature (°C)
                    </label>
                    <input
                      type="number"
                      value={endTemp}
                      onChange={(e) => setEndTemp(e.target.value)}
                      placeholder="120"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      step="0.1"
                      min="-273.15"
                      max="1000"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Temperature (°C)
                  </label>
                  <input
                    type="number"
                    value={temperature}
                    onChange={(e) => setTemperature(e.target.value)}
                    placeholder="Enter temperature (e.g., 25.5)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    step="0.1"
                    min="0"
                    max="200"
                  />
                </div>
              )}
            </div>

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={!isCameraActive || isAnalyzing || !temperature}
              className="w-full mt-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
            >
              {isAnalyzing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {mode === 'image' ? 'Capture & Analyze' : 'Capture Video & Analyze'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LiveAnalysisPage; 