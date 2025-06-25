import React, { useState } from 'react';
import './SettingsPage.css';

const SettingsPage = () => {
  const [apiKey, setApiKey] = useState('sk...');
  const [apiEndpoint, setApiEndpoint] = useState('https://api.example.com');
  const [emailNotif, setEmailNotif] = useState(false);
  const [browserNotif, setBrowserNotif] = useState(false);
  const [firstName, setFirstName] = useState('John');
  const [lastName, setLastName] = useState('Doe');

  return (
    <div className="settings-page">
      <h1 className="page-title">Settings</h1>
      <p className="subtitle">Configure your dashboard preferences and integrations</p>
      <div className="settings-grid">
        {/* API Configuration */}
        <div className="settings-card">
          <h2 className="settings-card-title">API Configuration</h2>
          <div className="settings-field">
            <label>OpenAI API Key</label>
            <input type="text" value={apiKey} onChange={e => setApiKey(e.target.value)} />
          </div>
          <div className="settings-field">
            <label>Custom API Endpoint</label>
            <input type="text" value={apiEndpoint} onChange={e => setApiEndpoint(e.target.value)} />
          </div>
          <button className="btn btn-primary settings-save-btn">Save API Settings</button>
        </div>
        {/* Notification Preferences */}
        <div className="settings-card">
          <h2 className="settings-card-title">Notification Preferences</h2>
          <div className="settings-field-row">
            <label>Email Notifications</label>
            <input type="checkbox" checked={emailNotif} onChange={e => setEmailNotif(e.target.checked)} />
            <span className="settings-switch-label">Receive email updates for completed analyses</span>
          </div>
          <div className="settings-field-row">
            <label>Browser Notifications</label>
            <input type="checkbox" checked={browserNotif} onChange={e => setBrowserNotif(e.target.checked)} />
            <span className="settings-switch-label">Show browser notifications for important updates</span>
          </div>
        </div>
        {/* User Profile */}
        <div className="settings-card">
          <h2 className="settings-card-title">User Profile</h2>
          <div className="settings-field">
            <label>First Name</label>
            <input type="text" value={firstName} onChange={e => setFirstName(e.target.value)} />
          </div>
          <div className="settings-field">
            <label>Last Name</label>
            <input type="text" value={lastName} onChange={e => setLastName(e.target.value)} />
          </div>
        </div>
        {/* Future Features */}
        <div className="settings-card future-feature" title="Coming soon!">
          <h2 className="settings-card-title">Integrations</h2>
          <p>Integrations with Slack, Teams, and more will be available soon.</p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 