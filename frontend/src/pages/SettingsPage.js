import React, { useState } from 'react';
import VectorizationManager from '../components/VectorizationManager';
import './SettingsPage.css';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('vectorization');
  const [apiKey, setApiKey] = useState('');
  const [apiEndpoint, setApiEndpoint] = useState('');
  const [emailNotif, setEmailNotif] = useState(false);
  const [browserNotif, setBrowserNotif] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const tabs = [
    { id: 'vectorization', label: 'Vectorization Manager', icon: '🧠' },
    { id: 'api', label: 'API Configuration', icon: '🔧' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'profile', label: 'User Profile', icon: '👤' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'vectorization':
        return <VectorizationManager />;
      
      case 'api':
        return (
          <div className="settings-content">
            <div className="settings-section">
              <h3>API Configuration</h3>
              <p className="settings-description">Configure your API keys and endpoints for AI services</p>
              
              <div className="settings-form">
                <div className="form-group">
                  <label className="form-label">OpenAI API Key</label>
                  <input 
                    type="password" 
                    value={apiKey} 
                    onChange={e => setApiKey(e.target.value)}
                    placeholder="sk-..."
                    className="form-input"
                  />
                  <small className="form-hint">Your OpenAI API key for AI-powered analysis</small>
                </div>
                
                <div className="form-group">
                  <label className="form-label">Custom API Endpoint</label>
                  <input 
                    type="url" 
                    value={apiEndpoint} 
                    onChange={e => setApiEndpoint(e.target.value)}
                    placeholder="https://api.example.com"
                    className="form-input"
                  />
                  <small className="form-hint">Optional: Custom endpoint for API requests</small>
                </div>
                
                <div className="form-actions">
                  <button className="btn btn-primary">Save API Settings</button>
                  <button className="btn btn-outline">Test Connection</button>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'notifications':
        return (
          <div className="settings-content">
            <div className="settings-section">
              <h3>Notification Preferences</h3>
              <p className="settings-description">Choose how you want to be notified about important updates</p>
              
              <div className="settings-form">
                <div className="notification-option">
                  <div className="notification-info">
                    <h4>Email Notifications</h4>
                    <p>Receive email updates for completed analyses and proposal generation</p>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      checked={emailNotif} 
                      onChange={e => setEmailNotif(e.target.checked)} 
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                
                <div className="notification-option">
                  <div className="notification-info">
                    <h4>Browser Notifications</h4>
                    <p>Show browser notifications for important updates and status changes</p>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox" 
                      checked={browserNotif} 
                      onChange={e => setBrowserNotif(e.target.checked)} 
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                
                <div className="form-actions">
                  <button className="btn btn-primary">Save Preferences</button>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'profile':
        return (
          <div className="settings-content">
            <div className="settings-section">
              <h3>User Profile</h3>
              <p className="settings-description">Manage your personal information and account details</p>
              
              <div className="settings-form">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">First Name</label>
                    <input 
                      type="text" 
                      value={firstName} 
                      onChange={e => setFirstName(e.target.value)}
                      placeholder="Enter first name"
                      className="form-input"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Last Name</label>
                    <input 
                      type="text" 
                      value={lastName} 
                      onChange={e => setLastName(e.target.value)}
                      placeholder="Enter last name"
                      className="form-input"
                    />
                  </div>
                </div>
                
                <div className="form-actions">
                  <button className="btn btn-primary">Update Profile</button>
                  <button className="btn btn-outline">Change Password</button>
                </div>
              </div>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="settings-page-enhanced">
      <div className="settings-header">
        <h1>Settings & Management</h1>
        <p>Configure your dashboard preferences and manage system components</p>
      </div>
      
      <div className="settings-container">
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`settings-nav-item ${activeTab === tab.id ? 'active' : ''}`}
              >
                <span className="nav-icon">{tab.icon}</span>
                <span className="nav-label">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
        
        <div className="settings-main">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 