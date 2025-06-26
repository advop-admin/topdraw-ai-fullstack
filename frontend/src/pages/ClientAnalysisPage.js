import React, { useState } from 'react';
import { clientAPI, projectAPI, proposalAPI } from '../services/api';
import ProgressBar from '../components/ProgressBar';
import './ClientAnalysisPage.css';

const ClientAnalysisPage = () => {
  // Form State
  const [clientName, setClientName] = useState('');
  const [clientUrl, setClientUrl] = useState('');
  const [socialUrls, setSocialUrls] = useState('');
  const [files, setFiles] = useState([]);
  
  // Process State
  const [currentStep, setCurrentStep] = useState(1); // 1: Form, 2: Analysis, 3: Projects, 4: Proposal
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Data State
  const [analysisResult, setAnalysisResult] = useState(null);
  const [recommendedProjects, setRecommendedProjects] = useState([]);
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [generatedProposal, setGeneratedProposal] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleAnalyze = async () => {
    if (!clientName.trim() || !clientUrl.trim()) {
      setError('Please enter client name and website URL');
      return;
    }
    
    setError(null);
    setIsLoading(true);
    setProgress(0);
    setCurrentStep(2);
    
    try {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 80));
      }, 1000);

      const formData = new FormData();
      formData.append('name', clientName);
      formData.append('website', clientUrl);
      
      const socialArr = socialUrls
        .split('\n')
        .map((url) => url.trim())
        .filter((url) => url.length > 0);
      formData.append('social_urls', JSON.stringify(socialArr));
      
      files.forEach((file) => formData.append('screenshots', file));

      // Step 1: Analyze Client
      const analysisResponse = await clientAPI.analyzeClient(formData);
      setAnalysisResult(analysisResponse.data);
      setProgress(90);

      // Step 2: Get Recommended Projects
      const projectsResponse = await projectAPI.getRecommendedProjects(analysisResponse.data);
      setRecommendedProjects(projectsResponse.data.projects || []);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        setIsLoading(false);
        setCurrentStep(3);
        setProgress(0);
      }, 500);

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
      setIsLoading(false);
      setCurrentStep(1);
      setProgress(0);
    }
  };

  const handleProjectSelection = (projectId) => {
    setSelectedProjects(prev => {
      if (prev.includes(projectId)) {
        return prev.filter(id => id !== projectId);
      } else {
        return [...prev, projectId];
      }
    });
  };

  const handleGenerateProposal = async () => {
    if (selectedProjects.length === 0) {
      setError('Please select at least one project');
      return;
    }

    setError(null);
    setIsLoading(true);
    setProgress(0);
    
    try {
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 15, 90));
      }, 800);

      const proposalData = {
        client_analysis: analysisResult,
        selected_projects: selectedProjects,
        client_name: clientName
      };

      const proposalResponse = await proposalAPI.generateProposal(proposalData);
      setGeneratedProposal(proposalResponse.data);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        setIsLoading(false);
        setCurrentStep(4);
        setProgress(0);
      }, 500);

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Proposal generation failed');
      setIsLoading(false);
    }
  };

  const handleProposalEdit = (sectionIndex, newContent) => {
    setGeneratedProposal(prev => ({
      ...prev,
      sections: prev.sections.map((section, index) => 
        index === sectionIndex ? { ...section, content: newContent } : section
      )
    }));
  };

  const handleSaveProposal = async () => {
    try {
      await proposalAPI.saveProposal(generatedProposal);
      alert('Proposal saved successfully!');
    } catch (err) {
      setError('Failed to save proposal');
    }
  };

  const handleExportProposal = () => {
    const proposalText = generatedProposal.sections
      .map(section => `${section.title}\n\n${section.content}`)
      .join('\n\n---\n\n');
    
    const blob = new Blob([proposalText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${clientName}_Proposal.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const resetWorkflow = () => {
    setCurrentStep(1);
    setAnalysisResult(null);
    setRecommendedProjects([]);
    setSelectedProjects([]);
    setGeneratedProposal(null);
    setError(null);
    setProgress(0);
  };

  const renderStepIndicator = () => (
    <div className="step-indicator">
      <div className={`step ${currentStep >= 1 ? 'completed' : ''} ${currentStep === 1 ? 'active' : ''}`}>
        <span className="step-number">1</span>
        <span className="step-label">Client Info</span>
      </div>
      <div className={`step ${currentStep >= 2 ? 'completed' : ''} ${currentStep === 2 ? 'active' : ''}`}>
        <span className="step-number">2</span>
        <span className="step-label">Analysis</span>
      </div>
      <div className={`step ${currentStep >= 3 ? 'completed' : ''} ${currentStep === 3 ? 'active' : ''}`}>
        <span className="step-number">3</span>
        <span className="step-label">Projects</span>
      </div>
      <div className={`step ${currentStep >= 4 ? 'completed' : ''} ${currentStep === 4 ? 'active' : ''}`}>
        <span className="step-number">4</span>
        <span className="step-label">Proposal</span>
      </div>
    </div>
  );

  const renderForm = () => (
    <div className="workflow-section">
      <div className="section-header">
        <h2>Client Information</h2>
        <p>Enter client details to begin analysis</p>
      </div>
      
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Client Name *</label>
          <input
            type="text"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            placeholder="Enter client company name"
            className="form-input"
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
          />
        </div>
        
        <div className="form-group full-width">
          <label className="form-label">Social Media URLs</label>
          <textarea
            value={socialUrls}
            onChange={(e) => setSocialUrls(e.target.value)}
            placeholder="LinkedIn, Twitter, Facebook URLs (one per line)"
            className="form-input"
            rows={3}
          />
        </div>
        
        <div className="form-group full-width">
          <label className="form-label">Screenshots & Documents</label>
          <div className="file-upload-area">
            <input
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.pdf"
              onChange={handleFileChange}
              id="file-upload"
              className="file-input"
            />
            <label htmlFor="file-upload" className="file-upload-label">
              <div className="upload-icon">📁</div>
              <div className="upload-text">
                <span>Drop files here or click to upload</span>
                <small>PNG, JPG, PDF up to 10MB each</small>
              </div>
            </label>
          </div>
          {files.length > 0 && (
            <div className="file-list">
              {files.map((file, idx) => (
                <div key={idx} className="file-item">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="form-actions">
        <button onClick={handleAnalyze} className="btn btn-primary btn-large">
          Start Analysis 🚀
        </button>
      </div>
    </div>
  );

  const renderAnalysisResults = () => (
    <div className="workflow-section">
      <div className="section-header">
        <h2>Analysis Results</h2>
        <p>Client data analysis completed</p>
      </div>
      
      <div className="analysis-display">
        <div className="analysis-card">
          <h3>Company Overview</h3>
          <div className="analysis-content">
            <div className="analysis-item">
              <strong>Industry:</strong> {analysisResult?.industry || 'N/A'}
            </div>
            <div className="analysis-item">
              <strong>Company Size:</strong> {analysisResult?.company_size || 'N/A'}
            </div>
            <div className="analysis-item">
              <strong>Technologies:</strong>
              <div className="tech-tags">
                {analysisResult?.technologies?.map((tech, idx) => (
                  <span key={idx} className="tech-tag">{tech}</span>
                )) || 'N/A'}
              </div>
            </div>
          </div>
        </div>
        
        <div className="analysis-card">
          <h3>Business Needs</h3>
          <div className="analysis-content">
            {analysisResult?.business_needs?.map((need, idx) => (
              <div key={idx} className="need-item">• {need}</div>
            )) || 'No specific needs identified'}
          </div>
        </div>
        
        <div className="analysis-card">
          <h3>Key Insights</h3>
          <div className="analysis-content">
            {analysisResult?.insights?.map((insight, idx) => (
              <div key={idx} className="insight-item">💡 {insight}</div>
            )) || 'No insights available'}
          </div>
        </div>
      </div>
    </div>
  );

  const renderRecommendedProjects = () => (
    <div className="workflow-section">
      <div className="section-header">
        <h2>Recommended Projects</h2>
        <p>Select relevant projects for proposal generation</p>
      </div>
      
      <div className="projects-grid">
        {recommendedProjects.map((project) => (
          <div 
            key={project.id} 
            className={`project-card ${selectedProjects.includes(project.id) ? 'selected' : ''}`}
            onClick={() => handleProjectSelection(project.id)}
          >
            <div className="project-header">
              <h3>{project.name}</h3>
              <div className="match-score">
                {project.match_score}% Match
              </div>
            </div>
            
            <div className="project-meta">
              <span className="project-industry">{project.industry}</span>
              <span className="project-date">{project.date}</span>
            </div>
            
            <div className="project-description">
              {project.description}
            </div>
            
            <div className="project-technologies">
              {project.technologies?.map((tech, idx) => (
                <span key={idx} className="tech-badge">{tech}</span>
              ))}
            </div>
            
            <div className="project-impact">
              <strong>Impact:</strong> {project.business_impact}
            </div>
            
            <div className="selection-indicator">
              {selectedProjects.includes(project.id) && (
                <span className="selected-icon">✓ Selected</span>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="form-actions">
        <button 
          onClick={handleGenerateProposal} 
          className="btn btn-primary btn-large"
          disabled={selectedProjects.length === 0}
        >
          Generate Proposal ({selectedProjects.length} projects selected)
        </button>
      </div>
    </div>
  );

  const renderProposal = () => (
    <div className="workflow-section">
      <div className="section-header">
        <h2>Generated Proposal</h2>
        <p>Edit and customize your proposal</p>
      </div>
      
      <div className="proposal-actions">
        <button onClick={handleSaveProposal} className="btn btn-secondary">
          💾 Save Proposal
        </button>
        <button onClick={handleExportProposal} className="btn btn-secondary">
          📥 Export as Text
        </button>
        <button onClick={resetWorkflow} className="btn btn-outline">
          🔄 New Analysis
        </button>
      </div>
      
      <div className="proposal-editor">
        {generatedProposal?.sections?.map((section, index) => (
          <div key={index} className="proposal-section">
            <div className="section-header">
              <h3>{section.title}</h3>
              <button className="btn btn-small">Regenerate Section</button>
            </div>
            <textarea
              value={section.content}
              onChange={(e) => handleProposalEdit(index, e.target.value)}
              className="proposal-textarea"
              rows={8}
            />
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="client-analysis-workflow">
      {renderStepIndicator()}
      
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
      
      {isLoading && (
        <div className="loading-section">
          <ProgressBar progress={progress} label={
            currentStep === 2 ? "Analyzing client data..." : "Generating proposal..."
          } />
        </div>
      )}
      
      {!isLoading && currentStep === 1 && renderForm()}
      {!isLoading && currentStep === 2 && renderAnalysisResults()}
      {!isLoading && currentStep === 3 && renderRecommendedProjects()}
      {!isLoading && currentStep === 4 && renderProposal()}
    </div>
  );
};

export default ClientAnalysisPage;