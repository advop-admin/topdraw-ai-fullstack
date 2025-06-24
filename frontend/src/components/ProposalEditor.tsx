import React from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

interface ProposalEditorProps {
  content: string;
  onChange: (content: string) => void;
}

const ProposalEditor: React.FC<ProposalEditorProps> = ({ content, onChange }) => {
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      ['link'],
      [{ 'align': [] }],
      ['clean']
    ],
  };

  const formats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'indent', 'link', 'align'
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-4 border-b">
        <h3 className="text-lg font-medium text-gray-900">Edit Proposal</h3>
        <p className="text-sm text-gray-600">Customize the generated proposal to match your needs</p>
      </div>
      <div className="p-4">
        <ReactQuill
          theme="snow"
          value={content}
          onChange={onChange}
          modules={modules}
          formats={formats}
          className="quill-editor"
          placeholder="Your proposal content will appear here..."
        />
      </div>
    </div>
  );
};

export default ProposalEditor; 