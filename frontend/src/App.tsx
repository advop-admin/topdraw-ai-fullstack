import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProposalGenerator from './pages/ProposalGenerator';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<ProposalGenerator />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 