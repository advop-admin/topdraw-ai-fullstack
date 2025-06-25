import React, { useState } from 'react';
import { clientAPI } from '../services/api';
import ProgressBar from '../components/ProgressBar';
import './ClientAnalysisPage.css';

const ClientAnalysisPage = () => {
  const [clientName, setClientName] = useState('');
  const [clientUrl, setClientUrl] = useState('');
  const [socialUrls, setSocialUrls] = useState('');
  const [notes, setNotes] = useState('');
  const [files, setFiles] = useState([]);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleAnalyze = async () => {
    if (!clientName.trim()) {
      setError('Please enter a client name');
      return;
    }
    if (!clientUrl.trim()) {
      setError('Please enter a client website URL');
      return;
    }
    setError(null);
    setIsLoading(true);
    setProgress(0);
    try {
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 1000);
      const formData = new FormData();
      formData.append('name', clientName);
      formData.append('website', clientUrl);
      // Social URLs as array of strings (one per line)
      const socialArr = socialUrls
        .split('\n')
        .map((url) => url.trim())
        .filter((url) => url.length > 0);
      formData.append('social_urls', JSON.stringify(socialArr));
      files.forEach((file) => formData.append('screenshots', file));
      // notes is a future field, not sent to backend
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
    <div className="client-analysis-page" style={{ background: 'var(--background-color)', minHeight: '100vh' }}>
      <h1 className="page-title">Client Analysis</h1>
      <p className="subtitle">Analyze client information to understand their business needs</p>
      <div className="analysis-cards-row">
        {/* Basic Info Card */}
        <div className="card analysis-card">
          <h2 className="card-title"><span role="img" aria-label="info">ℹ️</span> Basic Information</h2>
          <p className="card-desc">Provide basic details about your client</p>
          <div className="form-group">
            <label className="form-label">Client Name *</label>
            <input
              type="text"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              placeholder="Enter client company name"
              className="form-input"
              disabled={isLoading}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Website URL *</label>
            <input
              type="url"
              value={clientUrl}
              onChange={(e) => setClientUrl(e.target.value)}
              placeholder="https://example.com"
              className="form-input"
              disabled={isLoading}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Social Media URLs</label>
            <textarea
              value={socialUrls}
              onChange={(e) => setSocialUrls(e.target.value)}
              placeholder="LinkedIn, Twitter, Facebook URLs (one per line)"
              className="form-input"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <div className="form-group future-feature" title="Coming soon!">
            <label className="form-label">Additional Notes <span className="future-label">(Future)</span></label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any additional context about the client"
              className="form-input"
              rows={2}
              disabled
              style={{ opacity: 0.5, cursor: 'not-allowed' }}
            />
          </div>
        </div>
        {/* File Upload Card */}
        <div className="card analysis-card">
          <h2 className="card-title"><span role="img" aria-label="upload">📁</span> File Uploads</h2>
          <p className="card-desc">Upload screenshots, documents, or other relevant files</p>
          <div className="file-upload-box">
            <input
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.pdf"
              onChange={handleFileChange}
              disabled={isLoading}
              id="file-upload-input"
              style={{ display: 'none' }}
            />
            <label htmlFor="file-upload-input" className="file-upload-label">
              <div className="file-upload-dropzone">
                <div className="file-upload-icon">⬆️</div>
                <div>Drop Files here or click to upload</div>
                <div className="file-upload-hint">PNG, JPG, PDF up to 10MB each</div>
              </div>
            </label>
            {files.length > 0 && (
              <ul className="file-list">
                {files.map((file, idx) => (
                  <li key={idx}>{file.name}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
      {error && <div className="error-message">{error}</div>}
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
        className="btn btn-primary start-analysis-btn"
        style={{ margin: '2rem auto 0', display: 'block', minWidth: 200 }}
      >
        {isLoading ? 'Analyzing...' : 'Start Analysis'}
      </button>
      {analysisResult && (
        <div className="card analysis-results-card">
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