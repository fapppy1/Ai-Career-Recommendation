/**
 * Resume Upload Component
 * Proposal Alignment: Objective 3 - ML engine integration for user personalization
 * Handles PDF/DOCX/TXT upload, parsing, and skill auto-fill
 */

import React, { useState, useRef } from 'react';
import api from '../api/api';
import { toast } from 'react-hot-toast';

function ResumeUpload({ onParsed, onClose }) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const allowedExts = ['.pdf', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExts.includes(ext)) {
      toast.error('Please upload a PDF, DOCX, or TXT file');
      return;
    }
    
    // Validate size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
      toast.error('File size must be under 16MB');
      return;
    }
    
    setPreview({
      name: file.name,
      size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
      type: ext.toUpperCase()
    });
  };

  const handleUpload = async () => {
    if (!fileInputRef.current?.files[0]) {
      toast.error('Please select a file first');
      return;
    }
    
    setUploading(true);
    try {
      const result = await api.parseResume(fileInputRef.current.files[0]);
      
      if (result.success) {
        toast.success('Resume parsed successfully!');
        if (onParsed) {
          onParsed(result.data);
        }
        onClose?.();
      } else {
        toast.error(result.error || 'Failed to parse resume');
      }
    } catch (error) {
      toast.error(error.message || 'Upload failed - please try again');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">📄 Upload Your Resume</h3>
      <p className="text-sm text-gray-600 mb-6">
        Upload your resume (PDF, DOCX, or TXT) to automatically extract skills and experience.
      </p>
      
      {/* File Input */}
      <div className="mb-6">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".pdf,.docx,.txt"
          className="hidden"
          id="resume-upload"
        />
        <label
          htmlFor="resume-upload"
          className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:bg-gray-50 transition-colors"
        >
          <div className="text-center">
            <span className="text-3xl mb-2">📎</span>
            <p className="text-sm text-gray-600">
              Click to browse or drag & drop
            </p>
            <p className="text-xs text-gray-400 mt-1">PDF, DOCX, or TXT (max 16MB)</p>
          </div>
        </label>
      </div>

      {/* File Preview */}
      {preview && (
        <div className="mb-6 p-4 bg-blue-50 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-blue-900">{preview.name}</p>
              <p className="text-sm text-blue-700">{preview.size} • {preview.type}</p>
            </div>
            <button
              onClick={() => {
                setPreview(null);
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Remove
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleUpload}
          disabled={uploading || !preview}
          className={`flex-1 py-3 px-4 rounded-xl font-semibold text-white transition-colors ${
            uploading || !preview
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
          }`}
        >
          {uploading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              Parsing...
            </span>
          ) : (
            'Parse Resume'
          )}
        </button>
        <button
          onClick={onClose}
          disabled={uploading}
          className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-300 transition-colors"
        >
          Cancel
        </button>
      </div>

      {/* Privacy Note */}
      <p className="text-xs text-gray-500 mt-4 text-center">
        🔒 Your resume is processed locally and not stored on our servers. 
        Extracted skills are used only to personalize your recommendations.
      </p>
    </div>
  );
}

export default ResumeUpload;
