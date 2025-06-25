import React, { useState } from 'react';
import './ProjectManagementPage.css';

const mockProjects = [
  {
    id: 1,
    name: 'E-commerce Platform Redesign',
    match: 92,
    industry: 'E-commerce',
    date: 'Dec 2023',
    features: ['React', 'Node.js', 'MongoDB', 'Payment Integration', 'Mobile App'],
    impact: 'Increased conversion rate by 45% and reduced cart abandonment by 30%',
    business: 'Complete overhaul of an online retail platform with modern UI/UX',
  },
  {
    id: 2,
    name: 'Healthcare Management System',
    match: 87,
    industry: 'Healthcare',
    date: 'Nov 2023',
    features: ['Angular', 'PostgreSQL', 'HIPAA Compliance', 'API Integration'],
    impact: 'Reduced patient wait times by 60% and improved data accuracy by 95%',
    business: 'Digital transformation of patient management workflows',
  },
  {
    id: 3,
    name: 'Financial Analytics Dashboard',
    match: 78,
    industry: 'Finance',
    date: 'Oct 2023',
    features: ['Vue.js', 'Python', 'Machine Learning', 'Real-time Analytics'],
    impact: 'Enabled faster decision-making and reduced reporting time by 70%',
    business: 'Real-time financial data visualization and reporting platform',
  },
];

const ProjectManagementPage = () => {
  const [search, setSearch] = useState('');
  const filtered = mockProjects.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.industry.toLowerCase().includes(search.toLowerCase()) ||
    p.features.some(f => f.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="project-matching-page">
      <h1 className="page-title">Project Matching</h1>
      <p className="subtitle">Find similar historical projects to support your proposals</p>
      <div className="project-matching-header">
        <input
          className="project-search-input"
          type="text"
          placeholder="Search projects by name, industry, or technology..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="btn btn-secondary project-filter-btn future-feature" disabled title="Coming soon!">Filter</button>
      </div>
      <div className="project-matching-results">
        <h2 className="results-title">Project Matching Results</h2>
        <p className="results-desc">AI-matched historical projects based on client analysis</p>
        <div className="project-cards-row">
          {filtered.map(project => (
            <div className="project-card" key={project.id}>
              <div className="project-card-header">
                <div className="project-title">{project.name}</div>
                <div className="project-match" style={{ color: project.match > 85 ? '#10b981' : '#f59e0b' }}>
                  Match: <span className="match-score">{project.match}%</span>
                </div>
              </div>
              <div className="project-meta">
                <span className="project-industry">{project.industry}</span>
                <span className="project-date">{project.date}</span>
              </div>
              <div className="project-section">
                <div className="project-section-label">Key Features:</div>
                <div className="project-features">
                  {project.features.map((f, i) => (
                    <span className="feature-badge" key={i}>{f}</span>
                  ))}
                </div>
              </div>
              <div className="project-section">
                <div className="project-section-label">Business Impact:</div>
                <div className="project-impact">{project.impact}</div>
              </div>
              <div className="project-section">
                <div className="project-section-label">Description:</div>
                <div className="project-business">{project.business}</div>
              </div>
              <div className="project-card-actions">
                <button className="btn btn-link">View Details</button>
                <button className="btn btn-primary">Use for Proposal</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProjectManagementPage; 