import React, { useState } from 'react';
import { clientAPI } from '../services/api';
import ProgressBar from '../components/ProgressBar';
import './ClientAnalysisPage.css';

const ClientAnalysisPage = () => {
  const [clientUrl, setClientUrl] = useState('');
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [clientName, setClientName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleAnalyze = async () => {
    if (!clientName.trim()) {
      setError('Please enter a client name');
      return;
    }
    if (!clientUrl.trim()) {
      setError('Please enter a client URL');
      return;
    }

    setError(null);
    setIsLoading(true);
    setProgress(0);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 1000);

      // Create FormData for multipart/form-data
      const formData = new FormData();
      formData.append('name', clientName);
      formData.append('website', clientUrl);
      formData.append('social_urls', '[]'); // Empty array for now

      const result = await clientAPI.analyzeClient(formData);

      clearInterval(progressInterval);
      setProgress(100);
      
      setAnalysisResult(result.data);
      
      setTimeout(() => {
        setIsLoading(false);
        setProgress(0);
      }, 500);

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
      setIsLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="client-analysis-page">
      <h1 className="page-title">Client Analysis</h1>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Analyze New Client</h2>
        </div>
        
        <div className="form-content">
          <div className="form-group">
            <label className="form-label">
              Client Name
            </label>
            <input
              type="text"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              placeholder="Acme Corporation"
              className="form-input"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Client Website URL
            </label>
            <input
              type="url"
              value={clientUrl}
              onChange={(e) => setClientUrl(e.target.value)}
              placeholder="https://example.com"
              className="form-input"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Analysis Type
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="form-input"
              disabled={isLoading}
            >
              <option value="comprehensive">Comprehensive Analysis</option>
              <option value="basic">Basic Analysis</option>
            </select>
          </div>

          {error && (
            <div className="error-message">{error}</div>
          )}

          {isLoading && (
            <div className="loading-section">
              <ProgressBar progress={progress} label="Analyzing client..." />
              <p className="loading-text">
                This may take a few minutes. We're scraping the website and analyzing the data...
              </p>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={isLoading}
            className="btn btn-primary w-full"
          >
            {isLoading ? 'Analyzing...' : 'Start Analysis'}
          </button>
        </div>
      </div>

      {analysisResult && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Analysis Results</h2>
          </div>
          <div className="analysis-results">
            <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientAnalysisPage; 