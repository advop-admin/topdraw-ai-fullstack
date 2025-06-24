import React, { useState } from 'react';
import { ClientInfo } from '../types';
import { Plus, X, Upload } from 'lucide-react';

interface ClientInfoFormProps {
  onSubmit: (clientInfo: ClientInfo) => void;
  loading: boolean;
}

const ClientInfoForm: React.FC<ClientInfoFormProps> = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState<ClientInfo>({
    name: '',
    website: '',
    socialUrls: [''],
    screenshots: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.website) {
      alert('Please fill in required fields');
      return;
    }
    
    const cleanedData = {
      ...formData,
      socialUrls: formData.socialUrls.filter(url => url.trim() !== ''),
    };
    
    onSubmit(cleanedData);
  };

  const addSocialUrl = () => {
    setFormData(prev => ({
      ...prev,
      socialUrls: [...prev.socialUrls, ''],
    }));
  };

  const removeSocialUrl = (index: number) => {
    setFormData(prev => ({
      ...prev,
      socialUrls: prev.socialUrls.filter((_, i) => i !== index),
    }));
  };

  const updateSocialUrl = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      socialUrls: prev.socialUrls.map((url, i) => i === index ? value : url),
    }));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setFormData(prev => ({
      ...prev,
      screenshots: [...prev.screenshots, ...files],
    }));
  };

  const removeFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      screenshots: prev.screenshots.filter((_, i) => i !== index),
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Client Name */}
      <div>
        <label htmlFor="clientName" className="block text-sm font-medium text-gray-700 mb-2">
          Client Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="clientName"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-qburst-primary focus:border-qburst-primary"
          placeholder="Enter client company name"
          required
        />
      </div>

      {/* Website URL */}
      <div>
        <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
          Website URL <span className="text-red-500">*</span>
        </label>
        <input
          type="url"
          id="website"
          value={formData.website}
          onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-qburst-primary focus:border-qburst-primary"
          placeholder="https://example.com"
          required
        />
      </div>

      {/* Social URLs */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Social Media URLs
        </label>
        {formData.socialUrls.map((url, index) => (
          <div key={index} className="flex items-center space-x-2 mb-2">
            <input
              type="url"
              value={url}
              onChange={(e) => updateSocialUrl(index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-qburst-primary focus:border-qburst-primary"
              placeholder="https://linkedin.com/company/example"
            />
            {formData.socialUrls.length > 1 && (
              <button
                type="button"
                onClick={() => removeSocialUrl(index)}
                className="p-2 text-red-500 hover:text-red-700"
              >
                <X size={16} />
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addSocialUrl}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-qburst-primary"
        >
          <Plus className="mr-2" size={16} />
          Add Social URL
        </button>
      </div>

      {/* Screenshots Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Screenshots (Optional)
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <label htmlFor="screenshots" className="cursor-pointer">
              <span className="mt-2 block text-sm font-medium text-gray-900">
                Upload screenshots or images
              </span>
              <input
                id="screenshots"
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileUpload}
                className="sr-only"
              />
            </label>
            <p className="mt-1 text-xs text-gray-500">PNG, JPG, GIF up to 10MB each</p>
          </div>
        </div>

        {/* Uploaded Files List */}
        {formData.screenshots.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Uploaded Files:</h4>
            <div className="space-y-2">
              {formData.screenshots.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                  <span className="text-sm text-gray-700">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-qburst-primary hover:bg-qburst-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-qburst-primary disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze Client'}
        </button>
      </div>
    </form>
  );
};

export default ClientInfoForm; 