import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { id: 'client-analysis', label: 'Client Analysis', icon: '🔍', path: '/client-analysis' },
    { id: 'proposal-editor', label: 'Proposal Editor', icon: '✏️', path: '/proposal-editor' },
    { id: 'saved-proposals', label: 'Saved Proposals', icon: '📄', path: '/saved-proposals' },
    { id: 'project-management', label: 'Project Management', icon: '📊', path: '/project-management' },
    { id: 'settings', label: 'Settings', icon: '⚙️', path: '/settings' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">BDT Dashboard</h1>
        <p className="sidebar-subtitle">QBurst</p>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.id}
              to={item.path}
              className={`nav-item ${isActive ? 'nav-item-active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar; 