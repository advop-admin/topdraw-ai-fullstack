import React, { useState } from 'react';
import ClientInfoForm from '../components/ClientInfoForm';
import ProjectMatches from '../components/ProjectMatches';
import ProposalEditor from '../components/ProposalEditor';
import { ClientInfo, ProjectMatch, ScrapedData } from '../types';
import apiService from '../utils/api';
import { Download, Copy, Loader } from 'lucide-react';

const ProposalGenerator: React.FC = () => {
  const [step, setStep] = useState<'form' | 'analysis' | 'proposal'>('form');
  const [loading, setLoading] = useState(false);
  const [clientInfo, setClientInfo] = useState<ClientInfo | null>(null);
  const [scrapedData, setScrapedData] = useState<ScrapedData | null>(null);
  const [matchedProjects, setMatchedProjects] = useState<ProjectMatch[]>([]);
  const [proposalContent, setProposalContent] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleClientSubmit = async (info: ClientInfo) => {
    setLoading(true);
    setError('');
    
    try {
      const result = await apiService.analyzeClient(info);
      setClientInfo(info);
      setScrapedData(result.scraped_data);
      setMatchedProjects(result.matched_projects);
      setStep('analysis');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze client data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateProposal = async () => {
    if (!clientInfo || !scrapedData) return;
    
    setLoading(true);
    setError('');
    
    try {
      const proposal = await apiService.generateProposal({
        client_info: clientInfo,
        scraped_data: scrapedData,
        matched_projects: matchedProjects,
      });
      setProposalContent(proposal);
      setStep('proposal');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate proposal');
    } finally {
      setLoading(false);
    }
  };

  const downloadProposal = () => {
    const element = document.createElement('a');
    const file = new Blob([proposalContent], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${clientInfo?.name.replace(/\s+/g, '_')}_proposal.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const copyProposal = async () => {
    try {
      await navigator.clipboard.writeText(proposalContent);
      alert('Proposal copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy proposal:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-qburst-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">Q</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">QBurst Proposal Generator</h1>
                <p className="text-sm text-gray-600">AI-powered client analysis and proposal generation</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <div className={`w-3 h-3 rounded-full ${step === 'form' ? 'bg-qburst-primary' : 'bg-gray-300'}`}></div>
              <div className={`w-3 h-3 rounded-full ${step === 'analysis' ? 'bg-qburst-primary' : 'bg-gray-300'}`}></div>
              <div className={`w-3 h-3 rounded-full ${step === 'proposal' ? 'bg-qburst-primary' : 'bg-gray-300'}`}></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            <p className="font-medium">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-md flex items-center">
            <Loader className="animate-spin mr-2" size={20} />
            <p>Processing your request...</p>
          </div>
        )}

        {step === 'form' && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Client Information</h2>
            <ClientInfoForm onSubmit={handleClientSubmit} loading={loading} />
          </div>
        )}

        {step === 'analysis' && scrapedData && (
          <div className="space-y-6">
            {/* Scraped Data Summary */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Client Analysis Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Company Overview</h3>
                  <p className="text-sm text-gray-600 mb-4">{scrapedData.company_description}</p>
                  
                  <h3 className="font-medium text-gray-900 mb-2">Industry</h3>
                  <p className="text-sm text-gray-600 mb-4">{scrapedData.industry}</p>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Current Services</h3>
                  <ul className="text-sm text-gray-600 mb-4">
                    {scrapedData.services?.map((service: string, index: number) => (
                      <li key={index} className="mb-1">• {service}</li>
                    ))}
                  </ul>
                  
                  <h3 className="font-medium text-gray-900 mb-2">Technology Stack</h3>
                  <div className="flex flex-wrap gap-2">
                    {scrapedData.tech_stack?.map((tech: string, index: number) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Matched Projects */}
            <ProjectMatches projects={matchedProjects} />

            {/* Generate Proposal Button */}
            <div className="text-center">
              <button
                onClick={handleGenerateProposal}
                disabled={loading}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-qburst-primary hover:bg-qburst-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-qburst-primary disabled:opacity-50"
              >
                {loading ? <Loader className="animate-spin mr-2" size={20} /> : null}
                Generate Proposal
              </button>
            </div>
          </div>
        )}

        {step === 'proposal' && (
          <div className="space-y-6">
            {/* Action Buttons */}
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Generated Proposal</h2>
              <div className="flex space-x-3">
                <button
                  onClick={copyProposal}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-qburst-primary"
                >
                  <Copy className="mr-2" size={16} />
                  Copy
                </button>
                <button
                  onClick={downloadProposal}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-qburst-primary hover:bg-qburst-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-qburst-primary"
                >
                  <Download className="mr-2" size={16} />
                  Download
                </button>
              </div>
            </div>

            {/* Proposal Editor */}
            <ProposalEditor
              content={proposalContent}
              onChange={setProposalContent}
            />

            {/* Back Button */}
            <div className="text-center">
              <button
                onClick={() => setStep('form')}
                className="text-qburst-primary hover:text-qburst-secondary font-medium"
              >
                ← Start New Proposal
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ProposalGenerator; 