import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function FileAnalysisPage() {
  const navigate = useNavigate();
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [folderSupport, setFolderSupport] = useState(true);

  // Check if browser supports folder selection
  useEffect(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = '';
    setFolderSupport('webkitdirectory' in input);
  }, []);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      // Validate file types
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      const invalidFiles = files.filter(file => !validTypes.includes(file.type));
      
      if (invalidFiles.length > 0) {
        setError("Please select only valid image files (JPG, JPEG, or PNG).");
        setSelectedFiles([]);
        return;
      }
      
      setSelectedFiles(files);
      setError("");
    }
  };

  const handleFolderChange = (e) => {
    const files = Array.from(e.target.files);
    console.log("Folder files:", files); // Debug log
    
    if (files.length > 0) {
      // Filter for image files only
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      const imageFiles = files.filter(file => {
        const isValidType = validTypes.includes(file.type);
        const isValidExtension = /\.(jpg|jpeg|png)$/i.test(file.name);
        return isValidType || isValidExtension;
      });
      
      console.log("Valid image files:", imageFiles); // Debug log
      
      if (imageFiles.length === 0) {
        setError("No valid image files found in the selected folder. Please ensure the folder contains JPG, JPEG, or PNG files.");
        setSelectedFiles([]);
        return;
      }
      
      // For folder uploads, we need to create new File objects with sanitized names
      const sanitizedFiles = imageFiles.map((file, index) => {
        // Extract just the filename from the full path
        const pathParts = file.name.split(/[\/\\]/);
        const originalName = pathParts[pathParts.length - 1];
        
        // Create a new file with a sanitized name
        const sanitizedName = `folder_image_${index + 1}_${originalName}`;
        
        // Create a new File object with the sanitized name
        return new File([file], sanitizedName, {
          type: file.type,
          lastModified: file.lastModified
        });
      });
      
      setSelectedFiles(sanitizedFiles);
      setError("");
    } else {
      setError("No files found in the selected folder.");
      setSelectedFiles([]);
    }
  };

  const handleAnalyze = async () => {
    if (selectedFiles.length === 0) {
      setError("Please select at least one image file first.");
      return;
    }

    console.log("Starting analysis with files:", selectedFiles); // Debug log
    setIsAnalyzing(true);
    setError("");

    try {
      // Create form data
      const formData = new FormData();
      selectedFiles.forEach((file, index) => {
        console.log(`Adding file ${index + 1}:`, file.name, file.type, file.size); // Debug log
        formData.append('images', file);
      });

      console.log("FormData created, sending to backend..."); // Debug log
      console.log("Backend URL: http://localhost:5000/api/analyze"); // Debug log

      // Send to backend
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
        // Add headers to help with CORS
        headers: {
          'Accept': 'application/json',
        },
      });

      console.log("Response received:", response.status, response.statusText); // Debug log

      const data = await response.json();
      console.log("Response data:", data); // Debug log

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      // Navigate to results page with analysis data
      navigate('/results', { 
        state: { 
          analysisResults: data, 
          analysisType: "File Analysis" 
        } 
      });
    } catch (err) {
      console.error("Analysis error:", err);
      setError(err.message || "Failed to analyze images. Please try again.");
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
            <h1 className="text-3xl font-bold text-gray-800">📁 File Analysis</h1>
            <p className="text-gray-600 mt-2">Upload and analyze multiple microscope images</p>
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

        <div className="max-w-4xl mx-auto">
          {/* File Upload Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Image Selection</h2>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {/* File Selection Options */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Images
              </label>
              
              {/* Multiple File Selection */}
              <div className="mb-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".jpg,.jpeg,.png"
                    multiple
                    className="hidden"
                    id="file-input"
                  />
                  <label htmlFor="file-input" className="cursor-pointer">
                    <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-gray-600 mb-2">
                      Click to select multiple image files
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports JPG, JPEG, PNG formats
                    </p>
                  </label>
                </div>
              </div>

              {/* Folder Selection */}
              <div className="mb-4">
                <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  folderSupport 
                    ? 'border-green-300 hover:border-green-400' 
                    : 'border-gray-300 bg-gray-50'
                }`}>
                  {folderSupport ? (
                    <>
                      <input
                        type="file"
                        onChange={handleFolderChange}
                        accept=".jpg,.jpeg,.png"
                        multiple
                        webkitdirectory=""
                        directory=""
                        className="hidden"
                        id="folder-input"
                        onClick={(e) => {
                          // Clear the input value to allow selecting the same folder again
                          e.target.value = '';
                        }}
                      />
                      <label htmlFor="folder-input" className="cursor-pointer">
                        <svg className="w-12 h-12 mx-auto mb-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z" />
                        </svg>
                        <p className="text-gray-600 mb-2">
                          Click to select a folder with images
                        </p>
                        <p className="text-sm text-gray-500">
                          Will analyze all image files in the folder
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          (If folder selection doesn't work, use multiple file selection above)
                        </p>
                      </label>
                    </>
                  ) : (
                    <div className="text-gray-500">
                      <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <p className="text-gray-600 mb-2">
                        Folder selection not supported
                      </p>
                      <p className="text-sm text-gray-500">
                        Please use the multiple file selection above
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Selected Files Display */}
              {selectedFiles.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Selected Files ({selectedFiles.length})
                  </h4>
                  <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-lg p-2">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="text-sm text-gray-600 py-1 flex items-center">
                        <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {file.name}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Debug Info */}
            {selectedFiles.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-medium text-blue-800 mb-2">Debug Info:</h4>
                <div className="text-xs text-blue-700 space-y-1">
                  <p>Total files selected: {selectedFiles.length}</p>
                  <p>File types: {[...new Set(selectedFiles.map(f => f.type))].join(', ')}</p>
                  <p>Total size: {(selectedFiles.reduce((sum, f) => sum + f.size, 0) / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            )}

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={selectedFiles.length === 0 || isAnalyzing}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
            >
              {isAnalyzing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing {selectedFiles.length} image{selectedFiles.length !== 1 ? 's' : ''}...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Analyze {selectedFiles.length > 0 ? `${selectedFiles.length} Image${selectedFiles.length !== 1 ? 's' : ''}` : 'Images'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileAnalysisPage; 