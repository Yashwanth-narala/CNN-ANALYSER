import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import FileAnalysisPage from "./pages/FileAnalysisPage";
import HomePage from "./pages/HomePage";
import LiveAnalysisPage from "./pages/LiveAnalysisPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/live-analysis" element={<LiveAnalysisPage />} />
          <Route path="/file-analysis" element={<FileAnalysisPage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;