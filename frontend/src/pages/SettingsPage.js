import React, { useState } from 'react';
import VectorizationManager from '../components/VectorizationManager';
import './SettingsPage.css';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: 'General Settings' },
    { id: 'vectorization', label: 'Vectorization Management' },
    { id: 'api', label: 'API Configuration' },
    { id: 'system', label: 'System Status' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'vectorization':
        return <VectorizationManager />;
      case 'general':
        return (
          <div className="settings-section">
            <h3>General Settings</h3>
            <p>General application settings will be configured here.</p>
          </div>
        );
      case 'api':
        return (
          <div className="settings-section">
            <h3>API Configuration</h3>
            <p>API settings and configuration options will be available here.</p>
          </div>
        );
      case 'system':
        return (
          <div className="settings-section">
            <h3>System Status</h3>
            <p>System health and status information will be displayed here.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-container">
        <div className="settings-sidebar">
          <h2>Settings</h2>
          <nav className="settings-nav">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        
        <div className="settings-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 