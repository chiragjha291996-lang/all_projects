import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import './App.css';
import FileUpload from './components/FileUpload';
import ProcessingLoader from './components/ProcessingLoader';
import AnalysisResults from './components/AnalysisResults';
import ComprehensiveMetrics from './components/ComprehensiveMetrics';
import PageComparisonViewer from './components/PageComparisonViewer';
import { FileData, AnalysisResult, ProcessingJob } from './types';
import { checkBackendHealth } from './services/api';

// Main App Component with routing
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<MainApp />} />
          <Route path="/page-comparison/:doc1/:doc2" element={<PageComparisonRoute />} />
        </Routes>
      </div>
    </Router>
  );
}

// Page Comparison Route Component
function PageComparisonRoute() {
  const { doc1, doc2 } = useParams<{ doc1: string; doc2: string }>();
  const navigate = useNavigate();

  if (!doc1 || !doc2) {
    return <div>Invalid document parameters</div>;
  }

  return (
    <div className="page-comparison-container">
      <div className="navigation-header">
        <button 
          className="back-button"
          onClick={() => navigate('/')}
        >
          ← Back to Main App
        </button>
        <h1>SOP Insight Engine - Page Comparison</h1>
      </div>
      <PageComparisonViewer 
        doc1Name={decodeURIComponent(doc1)} 
        doc2Name={decodeURIComponent(doc2)} 
      />
    </div>
  );
}

// Main App Component (existing functionality)
function MainApp() {
  const [uploadedFiles, setUploadedFiles] = useState<FileData[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [processingJobs, setProcessingJobs] = useState<ProcessingJob[]>([]);
  const [showComprehensiveMetrics, setShowComprehensiveMetrics] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<{doc1: string, doc2: string} | null>(null);

  const handleFilesUploaded = (files: FileData[]) => {
    setUploadedFiles(files);
    setError(null);
    setAnalysisResult(null);
  };

  const handleJobsCreated = (jobs: ProcessingJob[]) => {
    setProcessingJobs(jobs);
  };

  const handleProcessingStart = () => {
    setIsProcessing(true);
    setError(null);
  };

  const handleProcessingComplete = (result: AnalysisResult) => {
    setIsProcessing(false);
    setAnalysisResult(result);
  };

  // Note: handleProcessingComplete is handled via custom event listener
  // const handleProcessingComplete = (result: AnalysisResult) => {
  //   setIsProcessing(false);
  //   setAnalysisResult(result);
  // };

  const handleError = (errorMessage: string) => {
    setIsProcessing(false);
    setError(errorMessage);
  };

  const resetAnalysis = () => {
    setUploadedFiles([]);
    setAnalysisResult(null);
    setError(null);
    setIsProcessing(false);
    setProcessingJobs([]);
    setShowComprehensiveMetrics(false);
    setSelectedDocuments(null);
  };

  const handleShowComprehensiveMetrics = (doc1: string, doc2: string) => {
    setSelectedDocuments({ doc1, doc2 });
    setShowComprehensiveMetrics(true);
  };

  // Check backend health on mount
  useEffect(() => {
    const checkBackend = async () => {
      const isOnline = await checkBackendHealth();
      setBackendStatus(isOnline ? 'online' : 'offline');
      if (!isOnline) {
        setError('Backend server is not running. Please ensure Flask server is running on port 5001.');
      }
    };
    
    checkBackend();
  }, []);

  // Listen for analysis completion from FileUpload component
  useEffect(() => {
    const handleAnalysisComplete = (event: any) => {
      setIsProcessing(false);
      setAnalysisResult(event.detail);
    };

    window.addEventListener('analysisComplete', handleAnalysisComplete);
    return () => {
      window.removeEventListener('analysisComplete', handleAnalysisComplete);
    };
  }, []);

  return (
    <div className="App">
      <header className="app-header">
        <h1>SOP Insight Engine</h1>
        <p>AI-Powered Standard Operating Procedure Analysis with Qwen 2.5</p>
        {backendStatus === 'checking' && (
          <div className="backend-status checking">Checking backend connection...</div>
        )}
        {backendStatus === 'online' && (
          <div className="backend-status online">✓ Backend connected</div>
        )}
        {backendStatus === 'offline' && (
          <div className="backend-status offline">⚠ Backend offline</div>
        )}
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)} className="close-button">×</button>
          </div>
        )}

        {!analysisResult && !isProcessing && (
          <FileUpload
            onFilesUploaded={handleFilesUploaded}
            onJobsCreated={handleJobsCreated}
            onProcessingStart={handleProcessingStart}
            onError={handleError}
            uploadedFiles={uploadedFiles}
          />
        )}

        {isProcessing && (
          <ProcessingLoader 
            jobs={processingJobs}
            onProcessingComplete={handleProcessingComplete}
            onError={handleError}
          />
        )}

        {analysisResult && !showComprehensiveMetrics && (
          <AnalysisResults
            result={analysisResult}
            onReset={resetAnalysis}
            onShowComprehensiveMetrics={handleShowComprehensiveMetrics}
          />
        )}

        {showComprehensiveMetrics && selectedDocuments && (
          <ComprehensiveMetrics
            doc1={selectedDocuments.doc1}
            doc2={selectedDocuments.doc2}
            onReset={resetAnalysis}
          />
        )}
      </main>
    </div>
  );
}

export default App;