import React, { useState } from 'react';
import './ProposalEditor.css';

const ProposalEditor = () => {
  const [content, setContent] = useState('');

  const handleSave = () => {
    // Placeholder save logic
    alert('Proposal saved!');
  };

  return (
    <div className="proposal-editor">
      <h2 className="editor-title">Proposal Editor</h2>
      <textarea
        className="editor-textarea"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write your proposal here..."
      />
      <button
        className="btn btn-primary"
        onClick={handleSave}
      >
        Save Proposal
      </button>
    </div>
  );
};

export default ProposalEditor; 