import React, { useState } from 'react';
import './ProposalEditor.css';

const mockSections = [
  {
    title: 'Executive Summary',
    desc: 'High-level overview of the proposed solution',
    content: 'Based on our analysis of your requirements and our experience with similar projects, we propose a comprehensive digital transformation solution...'
  },
  {
    title: 'Approach & Methodology',
    desc: 'Our proven methodology and approach',
    content: 'Our approach combines industry best practices with innovative technologies to deliver exceptional results...'
  },
  {
    title: 'Timeline & Milestones',
    desc: 'Project phases and key deliverables',
    content: 'Phase 1: Discovery & Planning (2 weeks)\nPhase 2: Design & Development (8 weeks)\nPhase 3: Testing & Deployment (2 weeks)'
  },
  {
    title: 'Investment & Resources',
    desc: 'Cost breakdown and team allocation',
    content: 'Total Investment: $150,000 - $200,000\nTimeline: 12 weeks\nTeam Size: 6-8 developers'
  },
];

const ProposalEditor = () => {
  const [sections, setSections] = useState(mockSections);

  const handleRegenerate = (idx) => {
    // Placeholder: just append ' (Regenerated)'
    setSections(sections => sections.map((s, i) => i === idx ? { ...s, content: s.content + ' (Regenerated)' } : s));
  };

  const handleRegenerateAll = () => {
    setSections(sections => sections.map(s => ({ ...s, content: s.content + ' (Regenerated)' })));
  };

  const handleCopyAll = () => {
    navigator.clipboard.writeText(sections.map(s => s.content).join('\n\n'));
    alert('Proposal copied to clipboard!');
  };

  const handleDownloadPDF = () => {
    // Placeholder: just alert
    alert('Download PDF (future feature)');
  };

  return (
    <div className="proposal-generation-page">
      <h1 className="page-title">Generated Proposal</h1>
      <div className="proposal-toolbar">
        <span className="proposal-status-label">Draft</span>
        <span className="proposal-updated-label">Last updated: 2 minutes ago</span>
        <button className="btn btn-secondary" onClick={handleCopyAll}>Copy All</button>
        <button className="btn btn-secondary future-feature" onClick={handleDownloadPDF} disabled title="Coming soon!">Download PDF</button>
        <button className="btn btn-primary" onClick={handleRegenerateAll}>Regenerate All</button>
      </div>
      <div className="proposal-sections-row">
        {sections.map((section, idx) => (
          <div className="proposal-section-card" key={idx}>
            <div className="proposal-section-header">
              <div className="proposal-section-title">{section.title}</div>
              <button className="btn btn-secondary" onClick={() => handleRegenerate(idx)}>Regenerate</button>
            </div>
            <div className="proposal-section-desc">{section.desc}</div>
            <textarea
              className="proposal-section-content"
              value={section.content}
              readOnly
              rows={5}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProposalEditor; 