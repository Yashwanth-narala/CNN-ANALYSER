import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import MetricGraph from "../components/MetricGraph";

function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedMetric, setSelectedMetric] = useState("Mean");
  const [analysisResults, setAnalysisResults] = useState(null);
  const [analysisType, setAnalysisType] = useState("");

  useEffect(() => {
    // Get analysis results from location state
    if (location.state && location.state.analysisResults) {
      setAnalysisResults(location.state.analysisResults);
      setAnalysisType(location.state.analysisType || "File Analysis");
    } else {
      // If no results, redirect back to home
      navigate('/');
    }
  }, [location.state, navigate]);

  const getGraphData = (metrics, label) => {
    if (!metrics || !metrics[label] || !metrics["Temperature"]) return [];
    return metrics[label].map((value, i) => ({
      temp: metrics["Temperature"][i],
      value: value,
    }));
  };

  const handleNewAnalysis = () => {
    navigate('/');
  };

  const handleBackToAnalysis = () => {
    if (analysisType === "Live Analysis") {
      navigate('/live-analysis');
    } else {
      navigate('/file-analysis');
    }
  };

  if (!analysisResults) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  const { metrics, transitions, csv_url, pdf_url } = analysisResults;
  const metricColors = {
    "Mean": "#3B82F6",
    "Std Deviation": "#10B981", 
    "RMS": "#F59E0B",
    "Entropy": "#EF4444",
    "Contrast": "#8B5CF6",
    "Energy": "#14B8A6"
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">📊 Analysis Results</h1>
            <p className="text-gray-600 mt-2">
              {analysisType} - {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleBackToAnalysis}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Analysis
            </button>
            <button
              onClick={handleNewAnalysis}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              New Analysis
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Images Analyzed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {metrics && metrics.Filename ? metrics.Filename.length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Analysis Status</p>
                <p className="text-2xl font-bold text-gray-900">Complete</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Metrics</p>
                <p className="text-2xl font-bold text-gray-900">6</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Transitions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {transitions ? Object.keys(transitions).length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Temperature Range</p>
                <p className="text-lg font-bold text-gray-900">
                  {metrics && metrics.Temperature ? 
                    `${Math.max(...metrics.Temperature).toFixed(1)}°C - ${Math.min(...metrics.Temperature).toFixed(1)}°C` : 
                    "N/A"
                  }
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Metrics Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Metrics Summary</h2>
              <div className="space-y-4">
                {Object.entries(metrics).map(([key, values]) => {
                  if (key === "Temperature" || key === "Filename") return null;
                  const value = Array.isArray(values) ? values[0] : values;
                  return (
                    <div key={key} className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm font-medium text-gray-600 mb-1">{key}</div>
                      <div className="text-lg font-bold text-gray-800">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Detailed Analysis */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Detailed Analysis</h2>
              
              {/* Metric Selection Dropdown */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Metric to Observe:
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                >
                  {Object.keys(metrics).map(key => {
                    if (key === "Temperature" || key === "Filename") return null;
                    return (
                      <option key={key} value={key}>{key}</option>
                    );
                  })}
                </select>
              </div>

              {/* Selected Metric Graph */}
              <div className="mb-8">
                <MetricGraph
                  title={`${selectedMetric} Analysis`}
                  data={getGraphData(metrics, selectedMetric)}
                  color={metricColors[selectedMetric] || "#3B82F6"}
                  transitionLines={transitions ? Object.values(transitions) : []}
                />
              </div>

              {/* Phase Transitions */}
              {transitions && Object.keys(transitions).length > 0 && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">🧬 Detected Phase Transitions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(transitions).map(([label, temp], i) => (
                      <div key={i} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="font-medium text-gray-700 mb-1">{label}</div>
                        <div className="text-2xl font-bold text-blue-600">{temp}°C</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Download Options */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => window.open(csv_url, '_blank')} 
                  className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-3 rounded-lg transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download CSV Report
                </button>
                <button 
                  onClick={() => window.open(pdf_url, '_blank')} 
                  className="flex-1 bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download PDF Report
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* All Metrics Graphs */}
        <div className="mt-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">All Metrics Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(metrics).map(([key, values]) => {
                if (key === "Temperature" || key === "Filename") return null;
                return (
                  <MetricGraph
                    key={key}
                    title={key}
                    data={getGraphData(metrics, key)}
                    color={metricColors[key] || "#3B82F6"}
                  />
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage; 