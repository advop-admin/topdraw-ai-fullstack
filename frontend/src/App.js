import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import StatusIndicator from './components/StatusIndicator';
import ClientAnalysisPage from './pages/ClientAnalysisPage';
import SavedProposalsPage from './pages/SavedProposalsPage';
import ProjectManagementPage from './pages/ProjectManagementPage';
import SettingsPage from './pages/SettingsPage';
import ProposalEditor from './components/ProposalEditor';
import './App.css';

const AppLayout = ({ children, title }) => {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <header className="app-header">
          <div className="header-content">
            <h1 className="page-title">{title}</h1>
            <StatusIndicator />
          </div>
        </header>
        <main className="app-main">
          {children}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Navigate to="/client-analysis" replace />} />
          <Route 
            path="/client-analysis" 
            element={
              <AppLayout title="Client Analysis">
                <ClientAnalysisPage />
              </AppLayout>
            } 
          />
          <Route 
            path="/proposal-editor" 
            element={
              <AppLayout title="Proposal Editor">
                <ProposalEditor />
              </AppLayout>
            } 
          />
          <Route 
            path="/saved-proposals" 
            element={
              <AppLayout title="Saved Proposals">
                <SavedProposalsPage />
              </AppLayout>
            } 
          />
          <Route 
            path="/project-management" 
            element={
              <AppLayout title="Project Management">
                <ProjectManagementPage />
              </AppLayout>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <AppLayout title="Settings">
                <SettingsPage />
              </AppLayout>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 