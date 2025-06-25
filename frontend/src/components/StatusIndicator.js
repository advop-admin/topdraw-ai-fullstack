import React, { useState, useEffect } from 'react';
import { systemAPI } from '../services/api';
import '../styles/components/status-indicator.css';

const StatusIndicator = () => {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await systemAPI.getHealth();
        setStatus('online');
      } catch (error) {
        setStatus('offline');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusText = () => {
    switch (status) {
      case 'online':
        return 'Backend Online';
      case 'offline':
        return 'Backend Offline';
      case 'checking':
        return 'Checking...';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="status-indicator">
      <div className={`status-dot ${status}`}></div>
      <span className="status-text">{getStatusText()}</span>
    </div>
  );
};

export default StatusIndicator; 