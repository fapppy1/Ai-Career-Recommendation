import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';
import { toast } from 'react-hot-toast';

function CybersecurityPage() {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('url-check');
  
  // Job Analysis State
  const [jobData, setJobData] = useState({ title: '', company: '', description: '', salary: '' });
  const [jobAnalysisResult, setJobAnalysisResult] = useState(null);
  const [analyzingJob, setAnalyzingJob] = useState(false);

  // Report Phishing State
  const [reportData, setReportData] = useState({ url: '', email: '', description: '' });
  const [reporting, setReporting] = useState(false);

  // URL Check State
  const [urlInput, setUrlInput] = useState('');
  const [urlResult, setUrlResult] = useState(null);
  const [checkingUrl, setCheckingUrl] = useState(false);

  // --- Handlers ---

  const handleJobAnalysis = async () => {
    if (!jobData.description) {
      toast.error("Please enter a job description to analyze.");
      return;
    }
    setAnalyzingJob(true);
    setJobAnalysisResult(null);
    try {
      const response = await api.analyzeJobPosting(jobData);
      if (response.success) {
        setJobAnalysisResult(response.analysis);
        toast.success("Job analysis complete!");
      }
    } catch (error) {
      toast.error("Failed to analyze job posting.");
    } finally {
      setAnalyzingJob(false);
    }
  };

  const handleReportPhishing = async () => {
    if (!reportData.url && !reportData.email) {
      toast.error("Please provide a URL or Email to report.");
      return;
    }
    setReporting(true);
    try {
      // Simulate reporting (backend endpoint for reporting is a future enhancement, currently we log locally)
      console.log("Phishing Report Submitted:", reportData);
      toast.success("Thank you! Your report has been submitted for review.");
      setReportData({ url: '', email: '', description: '' });
    } catch (error) {
      toast.error("Failed to submit report.");
    } finally {
      setReporting(false);
    }
  };

  const handleUrlCheck = async () => {
    if (!isAuthenticated) {
      toast.error("Please login to check URLs.");
      return;
    }
    if (!urlInput) return;
    setCheckingUrl(true);
    setUrlResult(null);
    try {
      const response = await api.checkUrlSafety(urlInput);
      if (response.success) {
        setUrlResult(response.result);
      }
    } catch (error) {
      toast.error("Failed to check URL.");
    } finally {
      setCheckingUrl(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🛡️ Cybersecurity Hub</h1>
        <p className="text-gray-600">Protect your job search with our advanced fraud detection tools.</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex justify-center mb-8 space-x-2">
        {[
          { id: 'url-check', label: '🔍 URL Safety Check' },
          { id: 'job-analyzer', label: '📋 Job Analyzer' },
          { id: 'report', label: '🚨 Report Phishing' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3 rounded-full font-medium transition-all duration-300 ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white shadow-lg scale-105'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* --- Tab Content --- */}
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 min-h-[400px]">
        
        {/* 1. URL Safety Check */}
        {activeTab === 'url-check' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Check if a Job URL is Safe</h2>
            <p className="text-sm text-gray-500 mb-6">Paste a URL from a job posting to check for malware or phishing indicators.</p>
            
            <div className="flex gap-2 mb-6">
              <input
                type="url"
                placeholder="https://suspicious-job-site.com/apply"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="flex-1 p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
              />
              <button
                onClick={handleUrlCheck}
                disabled={checkingUrl}
                className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition disabled:bg-gray-400"
              >
                {checkingUrl ? 'Scanning...' : 'Check Now'}
              </button>
            </div>

            {urlResult && (
              <div className={`p-6 rounded-xl border-2 ${urlResult.is_safe ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
                <h3 className={`text-2xl font-bold mb-2 ${urlResult.is_safe ? 'text-green-700' : 'text-red-700'}`}>
                  {urlResult.is_safe ? '✅ Safe Link' : '🚨 Dangerous Link'}
                </h3>
                <p className="text-gray-700">{urlResult.message}</p>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div>
                    <span className="font-semibold">Risk Level:</span> {urlResult.risk_level}
                  </div>
                  <div>
                    <span className="font-semibold">Confidence:</span> {urlResult.score}%
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 2. Job Analyzer */}
        {activeTab === 'job-analyzer' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Analyze Job Posting for Fraud</h2>
            <p className="text-sm text-gray-500 mb-6">Paste the job title and description. Our AI detects common scam patterns like "too good to be true" salary or urgency tactics.</p>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <input
                placeholder="Job Title (e.g. Data Entry Clerk)"
                value={jobData.title}
                onChange={(e) => setJobData({...jobData, title: e.target.value})}
                className="p-3 border border-gray-300 rounded-xl"
              />
              <input
                placeholder="Salary (e.g. $5000/week)"
                value={jobData.salary}
                onChange={(e) => setJobData({...jobData, salary: e.target.value})}
                className="p-3 border border-gray-300 rounded-xl"
              />
            </div>
            <textarea
              placeholder="Paste Job Description Here..."
              rows="5"
              value={jobData.description}
              onChange={(e) => setJobData({...jobData, description: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-xl mb-4"
            />
            
            <button
              onClick={handleJobAnalysis}
              disabled={analyzingJob}
              className="bg-purple-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-purple-700 transition disabled:bg-gray-400 w-full"
            >
              {analyzingJob ? 'Analyzing...' : 'Analyze Job'}
            </button>

            {jobAnalysisResult && (
              <div className={`mt-6 p-6 rounded-xl border-2 ${jobAnalysisResult.is_suspicious ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'}`}>
                <h3 className={`text-xl font-bold mb-3 ${jobAnalysisResult.is_suspicious ? 'text-red-700' : 'text-green-700'}`}>
                  {jobAnalysisResult.is_suspicious ? '⚠️ Suspicious Indicators Detected' : '✅ Job Appears Legitimate'}
                </h3>
                
                {jobAnalysisResult.red_flags && jobAnalysisResult.red_flags.length > 0 && (
                  <div className="mb-4">
                    <p className="font-semibold text-red-600 mb-1">Red Flags:</p>
                    <ul className="list-disc list-inside text-red-700 text-sm">
                      {jobAnalysisResult.red_flags.map((flag, i) => <li key={i}>{flag}</li>)}
                    </ul>
                  </div>
                )}
                
                {jobAnalysisResult.green_flags && jobAnalysisResult.green_flags.length > 0 && (
                  <div>
                    <p className="font-semibold text-green-600 mb-1">Positive Signs:</p>
                    <ul className="list-disc list-inside text-green-700 text-sm">
                      {jobAnalysisResult.green_flags.map((flag, i) => <li key={i}>{flag}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 3. Report Phishing */}
        {activeTab === 'report' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Report a Phishing Attempt</h2>
            <p className="text-sm text-gray-500 mb-6">Help the community stay safe. Report suspicious emails or links you've received.</p>
            
            <div className="space-y-4">
              <input
                placeholder="Suspicious URL (optional)"
                value={reportData.url}
                onChange={(e) => setReportData({...reportData, url: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-xl"
              />
              <input
                placeholder="Sender Email Address (optional)"
                value={reportData.email}
                onChange={(e) => setReportData({...reportData, email: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-xl"
              />
              <textarea
                placeholder="Describe what happened..."
                rows="4"
                value={reportData.description}
                onChange={(e) => setReportData({...reportData, description: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-xl"
              />
            </div>
            
            <button
              onClick={handleReportPhishing}
              disabled={reporting}
              className="mt-6 bg-red-500 text-white px-8 py-3 rounded-xl font-bold hover:bg-red-600 transition disabled:bg-gray-400 w-full"
            >
              {reporting ? 'Submitting...' : 'Submit Report'}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}

export default CybersecurityPage;