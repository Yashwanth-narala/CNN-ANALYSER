import { useState } from "react";

function FileUploader({ onAnalysisComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [startTemp, setStartTemp] = useState("");
  const [endTemp, setEndTemp] = useState("");
  const [useTemperatureRange, setUseTemperatureRange] = useState(false);

  const handleChange = (e) => {
    setFiles([...e.target.files]);
  };

  const handleAnalyze = async () => {
    if (files.length === 0) {
      alert("Please select image files first.");
      return;
    }
    
    // Validate file types
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    const invalidFiles = files.filter(file => !validTypes.includes(file.type));
    if (invalidFiles.length > 0) {
      alert("Please select only JPG, JPEG, or PNG image files.");
      return;
    }

    // Validate temperature range if enabled
    if (useTemperatureRange) {
      if (!startTemp || !endTemp) {
        alert("Please enter both start and end temperatures.");
        return;
      }
      
      const start = parseFloat(startTemp);
      const end = parseFloat(endTemp);
      
      if (isNaN(start) || isNaN(end)) {
        alert("Please enter valid numbers for temperatures.");
        return;
      }
      
      if (start < -273.15 || end < -273.15) {
        alert("Temperature cannot be below absolute zero (-273.15°C).");
        return;
      }
      
      if (start > 1000 || end > 1000) {
        alert("Temperature cannot exceed 1000°C.");
        return;
      }
    }
    
    setUploading(true);

    const formData = new FormData();
    files.forEach(file => formData.append("images", file));

    // Add temperature range parameters if enabled
    if (useTemperatureRange) {
      formData.append("start_temp", startTemp);
      formData.append("end_temp", endTemp);
    }

    try {
      const res = await fetch("http://localhost:5000/api/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        alert(`Error: ${data.error || 'Unknown error'}`);
        return;
      }

      onAnalysisComplete(data);
    } catch (err) {
      console.error("Upload error:", err);
      alert("Failed to analyze images. Please check if the backend server is running.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 mb-6">
      <div className="text-center">
        <div className="mb-4">
          <input 
            type="file" 
            multiple 
            onChange={handleChange} 
            accept=".jpg,.png,.jpeg" 
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        <div className="text-sm text-gray-500 mb-4">
          {files.length > 0 ? `Selected ${files.length} file(s)` : "No files selected"}
        </div>

        {/* Temperature Range Section */}
        <div className="mb-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center justify-center mb-3">
            <input
              type="checkbox"
              id="useTemperatureRange"
              checked={useTemperatureRange}
              onChange={(e) => setUseTemperatureRange(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="useTemperatureRange" className="text-sm font-medium text-gray-700">
              Use Temperature Range (instead of filename-based temperatures)
            </label>
          </div>
          
          {useTemperatureRange && (
            <div className="flex items-center justify-center gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Temperature (°C)
                </label>
                <input
                  type="number"
                  value={startTemp}
                  onChange={(e) => setStartTemp(e.target.value)}
                  placeholder="80"
                  className="w-24 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  step="0.1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Temperature (°C)
                </label>
                <input
                  type="number"
                  value={endTemp}
                  onChange={(e) => setEndTemp(e.target.value)}
                  placeholder="120"
                  className="w-24 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  step="0.1"
                />
              </div>
            </div>
          )}
        </div>

        <button 
          onClick={handleAnalyze} 
          disabled={uploading || files.length === 0}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
        >
          {uploading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Analyzing...
            </span>
          ) : "Analyze Images"}
        </button>
      </div>
    </div>
  );
}

export default FileUploader;
