import React from 'react';
import './SavedProposalsPage.css';

const analyses = [
  {
    id: 1,
    client: 'TechCorp Solutions',
    date: '2024-01-15',
    status: 'Completed',
    matched: 3,
    proposal: true,
  },
  {
    id: 2,
    client: 'Digital Innovations Ltd',
    date: '2024-01-12',
    status: 'In Progress',
    matched: 5,
    proposal: false,
  },
  {
    id: 3,
    client: 'StartupX',
    date: '2024-01-10',
    status: 'Completed',
    matched: 2,
    proposal: true,
  },
];

const SavedProposalsPage = () => {
  return (
    <div className="saved-proposals-page">
      <h1 className="page-title">Analysis History</h1>
      <p className="subtitle">Review past client analyses and generated proposals</p>
      <div className="card analysis-history-card">
        <h2 className="card-title">Recent Analyses</h2>
        <p className="card-desc">Your client analysis and proposal generation history</p>
        <table className="analyses-table">
          <thead>
            <tr>
              <th>Client Name</th>
              <th>Analysis Date</th>
              <th>Status</th>
              <th>Matched Projects</th>
              <th>Proposal</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {analyses.map((a) => (
              <tr key={a.id}>
                <td>{a.client}</td>
                <td>{a.date}</td>
                <td>
                  <span className={`status-badge status-${a.status.replace(/\s/g, '').toLowerCase()}`}>{a.status}</span>
                </td>
                <td>{a.matched}</td>
                <td>
                  {a.proposal ? (
                    <span className="proposal-generated">&#128196; Generated</span>
                  ) : (
                    <span className="proposal-not-generated">Not generated</span>
                  )}
                </td>
                <td>
                  <button className="btn btn-link">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SavedProposalsPage; 