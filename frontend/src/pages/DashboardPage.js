import React from 'react';
import './DashboardPage.css';

const stats = [
  { label: 'Total Analyses', value: 156, change: '+12% from last month' },
  { label: 'Proposals Generated', value: 128, change: '+8% from last month' },
  { label: 'Success Rate', value: '78%', change: '+3% from last month' },
  { label: 'Avg. Processing Time', value: '4.2m', change: '-0.5m from last month' },
];

const recentActivity = [
  { client: 'TechStart Inc.', action: 'Analysis completed', status: 'success', time: '2 hours ago' },
  { client: 'Healthcare Plus', action: 'Proposal generated', status: 'success', time: '4 hours ago' },
  { client: 'RetailCorp', action: 'Project matched', status: 'pending', time: '1 day ago' },
];

const DashboardPage = () => {
  return (
    <div className="dashboard-page">
      <div className="dashboard-stats-row">
        {stats.map((stat, idx) => (
          <div className="dashboard-stat-card" key={idx}>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
            <div className="stat-change">{stat.change}</div>
          </div>
        ))}
      </div>
      <div className="dashboard-actions-row">
        <div className="dashboard-action-card">
          <button className="btn btn-primary dashboard-action-btn">+ New Client Analysis</button>
        </div>
        <div className="dashboard-action-card future-feature" title="Coming soon!">
          <button className="btn btn-primary dashboard-action-btn" disabled>View Recent Proposals</button>
        </div>
        <div className="dashboard-action-card future-feature" title="Coming soon!">
          <button className="btn btn-primary dashboard-action-btn" disabled>Analytics Dashboard</button>
        </div>
      </div>
      <div className="dashboard-main-row">
        <div className="dashboard-main-col">
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Monthly Performance</h2>
            {/* Placeholder for chart */}
            <div className="dashboard-chart-placeholder future-feature" title="Coming soon!">
              <div style={{height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#b6c2d6'}}>Chart will appear here</div>
            </div>
          </div>
        </div>
        <div className="dashboard-main-col">
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Recent Activity</h2>
            <ul className="dashboard-activity-list">
              {recentActivity.map((item, idx) => (
                <li key={idx} className="dashboard-activity-item">
                  <span className="activity-client">{item.client}</span>
                  <span className={`activity-status status-${item.status}`}>{item.action}</span>
                  <span className="activity-time">{item.time}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 