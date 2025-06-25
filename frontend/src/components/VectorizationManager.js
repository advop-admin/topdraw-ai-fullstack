import React, { useState, useEffect } from 'react';
import { systemAPI } from '../services/api';
import './VectorizationManager.css';

const VectorizationManager = () => {
  const [chromaStats, setChromaStats] = useState(null);
  const [vectorizationStatus, setVectorizationStatus] = useState('idle');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRun, setLastRun] = useState(null);

  useEffect(() => {
    loadChromaStats();
    loadVectorizationStatus();
  }, []);

  const loadChromaStats = async () => {
    try {
      const response = await systemAPI.getChromaStats();
      setChromaStats(response.data);
    } catch (err) {
      console.error('Error loading ChromaDB stats:', err);
    }
  };

  const loadVectorizationStatus = async () => {
    try {
      const response = await systemAPI.getVectorizationStatus();
      setVectorizationStatus(response.data.status);
      setLastRun(response.data.last_run);
    } catch (err) {
      console.error('Error loading vectorization status:', err);
    }
  };

  const handleTriggerVectorization = async () => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await systemAPI.triggerVectorization();
      
      if (response.data.status === 'started') {
        setVectorizationStatus('running');
        setLastRun(new Date().toISOString());
        
        // Poll for completion
        pollVectorizationStatus();
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to trigger vectorization');
      setIsLoading(false);
    }
  };

  const pollVectorizationStatus = () => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await systemAPI.getVectorizationStatus();
        const status = response.data.status;
        
        if (status === 'idle' || status === 'completed') {
          setVectorizationStatus('idle');
          setIsLoading(false);
          loadChromaStats(); // Refresh stats
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Error polling vectorization status:', err);
        clearInterval(pollInterval);
        setIsLoading(false);
      }
    }, 5000); // Poll every 5 seconds

    // Stop polling after 10 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      setIsLoading(false);
      setVectorizationStatus('idle');
    }, 600000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'status-running';
      case 'completed':
        return 'status-completed';
      case 'error':
        return 'status-error';
      default:
        return 'status-idle';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'running':
        return 'Vectorization in Progress';
      case 'completed':
        return 'Vectorization Completed';
      case 'error':
        return 'Vectorization Failed';
      default:
        return 'Ready for Vectorization';
    }
  };

  return (
    <div className="vectorization-manager">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Vectorization Management</h2>
        </div>
        
        <div className="card-content">
          {/* ChromaDB Stats */}
          <div className="stats-section">
            <h3>ChromaDB Statistics</h3>
            {chromaStats ? (
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Collection:</span>
                  <span className="stat-value">{chromaStats.collection_name}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Documents:</span>
                  <span className="stat-value">{chromaStats.document_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Status:</span>
                  <span className={`stat-value status-${chromaStats.status}`}>
                    {chromaStats.status}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Deployment:</span>
                  <span className="stat-value">{chromaStats.deployment_type}</span>
                </div>
              </div>
            ) : (
              <p>Loading ChromaDB statistics...</p>
            )}
          </div>

          {/* Vectorization Status */}
          <div className="vectorization-section">
            <h3>Vectorization Status</h3>
            <div className="status-display">
              <div className={`status-indicator ${getStatusColor(vectorizationStatus)}`}>
                <span className="status-dot"></span>
                <span className="status-text">{getStatusText(vectorizationStatus)}</span>
              </div>
              
              {lastRun && (
                <div className="last-run">
                  <span className="label">Last Run:</span>
                  <span className="value">{new Date(lastRun).toLocaleString()}</span>
                </div>
              )}
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <div className="action-section">
              <button
                onClick={handleTriggerVectorization}
                disabled={isLoading || vectorizationStatus === 'running'}
                className={`btn btn-primary ${isLoading ? 'loading' : ''}`}
              >
                {isLoading ? (
                  <>
                    <span className="spinner"></span>
                    Running Vectorization...
                  </>
                ) : (
                  'Trigger Vectorization'
                )}
              </button>
              
              <button
                onClick={loadChromaStats}
                disabled={isLoading}
                className="btn btn-secondary"
              >
                Refresh Stats
              </button>
            </div>
          </div>

          {/* Information */}
          <div className="info-section">
            <h3>About Vectorization</h3>
            <p>
              Vectorization migrates project data from PostgreSQL to ChromaDB for AI-powered 
              similarity search. This process enables the system to find relevant projects 
              when analyzing new clients.
            </p>
            <ul>
              <li>Fetches all projects from the database</li>
              <li>Creates embeddings for similarity search</li>
              <li>Stores data in ChromaDB vector database</li>
              <li>Enables AI-powered project matching</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VectorizationManager; 