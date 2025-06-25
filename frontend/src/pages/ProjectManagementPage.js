import React from 'react';
import './ProjectManagementPage.css';

const ProjectManagementPage = () => {
  // Placeholder projects
  const projects = [
    { id: 1, name: 'AI Chatbot', status: 'Active' },
    { id: 2, name: 'Data Pipeline', status: 'Archived' },
  ];

  return (
    <div className="project-management-page">
      <h1 className="page-title">Project Management</h1>
      <div className="card">
        <table className="projects-table">
          <thead>
            <tr>
              <th className="table-header">Project Name</th>
              <th className="table-header">Status</th>
              <th className="table-header">Actions</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id} className="table-row">
                <td className="table-cell">{project.name}</td>
                <td className="table-cell">
                  <span className={`status-badge status-${project.status.toLowerCase()}`}>
                    {project.status}
                  </span>
                </td>
                <td className="table-cell">
                  <button className="btn btn-link">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProjectManagementPage; 