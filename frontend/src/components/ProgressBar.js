import React from 'react';
import '../styles/components/progress-bar.css';

const ProgressBar = ({ 
  progress, 
  label, 
  showPercentage = true 
}) => {
  return (
    <div className="progress-container">
      {label && (
        <div className="progress-label">
          <span className="progress-text">{label}</span>
          {showPercentage && (
            <span className="progress-percentage">{Math.round(progress)}%</span>
          )}
        </div>
      )}
      <div className="progress-container">
        <div
          className="progress-bar"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ProgressBar; 