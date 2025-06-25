import React from 'react';
import './SavedProposalsPage.css';

const SavedProposalsPage = () => {
  // Placeholder proposals
  const proposals = [
    { id: 1, title: 'Proposal for Acme Corp', date: '2024-06-01' },
    { id: 2, title: 'Proposal for Globex Inc', date: '2024-06-03' },
  ];

  return (
    <div className="saved-proposals-page">
      <h1 className="page-title">Saved Proposals</h1>
      <div className="card">
        <table className="proposals-table">
          <thead>
            <tr>
              <th className="table-header">Title</th>
              <th className="table-header">Date</th>
              <th className="table-header">Actions</th>
            </tr>
          </thead>
          <tbody>
            {proposals.map((proposal) => (
              <tr key={proposal.id} className="table-row">
                <td className="table-cell">{proposal.title}</td>
                <td className="table-cell">{proposal.date}</td>
                <td className="table-cell">
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