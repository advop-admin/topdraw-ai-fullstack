import React from 'react';
import { ProjectMatch } from '../types';
import { Star, Users, Clock, DollarSign } from 'lucide-react';

interface ProjectMatchesProps {
  projects: ProjectMatch[];
}

const ProjectMatches: React.FC<ProjectMatchesProps> = ({ projects }) => {
  if (projects.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Matched Projects</h2>
        <p className="text-gray-600">No matching projects found.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Recommended Projects</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div key={project.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-medium text-gray-900 text-sm leading-tight">{project.project_name}</h3>
              <div className="flex items-center space-x-1 text-yellow-500">
                <Star size={14} fill="currentColor" />
                <span className="text-xs font-medium">{(project.similarity_score * 100).toFixed(0)}%</span>
              </div>
            </div>

            {/* Description */}
            <p className="text-xs text-gray-600 mb-3 line-clamp-3">{project.project_description}</p>

            {/* Metadata */}
            <div className="space-y-2 mb-3">
              <div className="flex items-center text-xs text-gray-500">
                <span className="font-medium mr-1">Industry:</span>
                <span>{project.industry_vertical}</span>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <span className="font-medium mr-1">Client Type:</span>
                <span>{project.client_type}</span>
              </div>
            </div>

            {/* Key Features */}
            {project.key_features && project.key_features.length > 0 && (
              <div className="mb-3">
                <h4 className="text-xs font-medium text-gray-700 mb-1">Key Features:</h4>
                <ul className="text-xs text-gray-600">
                  {project.key_features.slice(0, 3).map((feature, index) => (
                    <li key={index} className="mb-1">• {feature}</li>
                  ))}
                  {project.key_features.length > 3 && (
                    <li className="text-gray-500">+ {project.key_features.length - 3} more</li>
                  )}
                </ul>
              </div>
            )}

            {/* Business Impact */}
            {project.business_impact && (
              <div className="bg-green-50 border border-green-200 rounded-md p-2">
                <h4 className="text-xs font-medium text-green-800 mb-1">Business Impact:</h4>
                <p className="text-xs text-green-700">{project.business_impact}</p>
              </div>
            )}

            {/* Tech Stack */}
            {project.tech_stack && (
              <div className="mt-3">
                <h4 className="text-xs font-medium text-gray-700 mb-1">Tech Stack:</h4>
                <div className="flex flex-wrap gap-1">
                  {Object.values(project.tech_stack).flat().slice(0, 4).map((tech: any, index: number) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-md">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectMatches; 