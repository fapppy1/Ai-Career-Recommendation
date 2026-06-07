/**
 * Security Panel Component
 * Proposal Alignment: Objectives 2, 5 - Cybersecurity awareness + phishing detection
 * Integrates real VirusTotal/URLScan.io results with heuristic fallback
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';
import { toast } from 'react-hot-toast';

function SecurityPanel({ initialUrl = '' }) {
  const { isAuthenticated } = useAuth();
  const [urlInput, setUrlInput] = useState(initialUrl);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState(null);
  const [tipCategory, setTipCategory] = useState('job_search');
  const [tip, setTip] = useState('');
  const [jobData, setJobData] = useState({
    title: '', company: '', description: '', salary: '', contact_email: ''
  });
  const [analyzingJob, setAnalyzingJob] = useState(false);
  const [jobResult, setJobResult] = useState(null);

  // Fetch security tip on mount and category change
  useEffect(() => {
    fetchTip();
  }, [tipCategory]);

  const fetchTip = async () => {
    try {
      const response = await api.getSecurityTips(tipCategory);
      if (response.success) {
        setTip(response.tip);
      }
    } catch (error) {
      console.error('Failed to fetch tip:', error);
    }
  };

  const checkUrl = async () => {
    if (!urlInput.trim()) {
      toast.error('Please enter a URL to check');
      return;
    }

    if (!isAuthenticated) {
      toast.error('Please sign in to check URL safety');
      return;
    }

    setChecking(true);
    setResult(null);

    try {
      const response = await api.checkUrlSafety(urlInput);
      if (response.success) {
        setResult(response.result);
        
        // Show contextual toast
        const messages = {
          'critical': '🚨 CRITICAL: Do not click this link!',
          'high': '⚠️ HIGH RISK: Exercise extreme caution',
          'medium': '⚠️ MEDIUM RISK: Verify before proceeding',
          'low': '✅ LOW RISK: URL appears safe',
          'unknown': '❓ Unable to verify - proceed with caution'
        };
        toast(messages[response.result.risk_level] || messages.unknown, {
          duration: 6000,
          style: {
            background: response.result.is_safe ? '#10B981' : '#EF4444',
            color: '#fff'
          }
        });
      }
    } catch (error) {
      toast.error(error.message || 'Failed to check URL');
    } finally {
      setChecking(false);
    }
  };

  const analyzeJob = async () => {
    if (!jobData.title || !jobData.description) {
      toast.error('Please fill in job title and description');
      return;
    }

    setAnalyzingJob(true);
    setJobResult(null);

    try {
      const response = await api.analyzeJobPosting(jobData);
      if (response.success) {
        setJobResult(response.analysis);
        toast.success('Job analysis complete!');
      }
    } catch (error) {
      toast.error(error.message || 'Failed to analyze job');
    } finally {
      setAnalyzingJob(false);
    }
  };

  const getRiskColor = (level) => {
    const colors = {
      'critical': 'from-red-100 to-rose-100 border-red-300 text-red-800',
      'high': 'from-orange-100 to-red-100 border-orange-300 text-orange-800',
      'medium': 'from-yellow-100 to-amber-100 border-yellow-300 text-yellow-800',
      'low': 'from-green-100 to-emerald-100 border-green-300 text-green-800',
      'unknown': 'from-gray-100 to-slate-100 border-gray-300 text-gray-800'
    };
    return colors[level] || colors.unknown;
  };

  const getRiskIcon = (level) => {
    const icons = {
      'critical': '🛑',
      'high': '🚨',
      'medium': '⚠️',
      'low': '✅',
      'unknown': '❓'
    };
    return icons[level] || icons.unknown;
  };

  return (
    <div className="space-y-6">
      {/* Security Tips Section */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">💡 Security Tip</h3>
          <select
            value={tipCategory}
            onChange={(e) => setTipCategory(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="job_search">Job Search</option>
            <option value="phishing_awareness">Phishing</option>
            <option value="data_privacy">Data Privacy</option>
            <option value="url_safety">URL Safety</option>
          </select>
        </div>
        
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 mb-3">
          <p className="text-gray-800">{tip || 'Loading tip...'}</p>
        </div>
        
        <button
          onClick={fetchTip}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Get another tip →
        </button>
      </div>

      {/* URL Safety Checker */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">🔍 Check Job URL Safety</h3>
        <p className="text-gray-600 mb-4 text-sm">
          Paste a job posting URL to check for phishing indicators using VirusTotal & URLScan.io
        </p>
        
        <div className="flex gap-2 mb-4">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://example-job-site.com/posting"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 text-sm"
            onKeyPress={(e) => e.key === 'Enter' && checkUrl()}
          />
          <button
            onClick={checkUrl}
            disabled={checking || !isAuthenticated}
            className={`px-6 py-3 rounded-xl font-semibold text-white transition-colors text-sm ${
              checking || !isAuthenticated
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {checking ? 'Checking...' : 'Check'}
          </button>
        </div>

        {/* URL Check Result */}
        {result && (
          <div className={`rounded-xl border-2 p-4 ${getRiskColor(result.risk_level)}`}>
            <div className="flex items-start gap-3">
              <span className="text-2xl">{getRiskIcon(result.risk_level)}</span>
              <div className="flex-1">
                <h4 className="font-semibold">{result.message}</h4>
                
                {/* API Results */}
                {Object.keys(result.api_results || {}).length > 0 && (
                  <div className="mt-2 text-xs space-y-1">
                    {result.api_results.virustotal && (
                      <p>• VirusTotal: {result.api_results.virustotal.malicious} malicious detections</p>
                    )}
                    {result.api_results.urlscan && (
                      <p>• URLScan.io: {result.api_results.urlscan.phishing ? 'Phishing detected' : 'Clean'}</p>
                    )}
                  </div>
                )}
                
                {/* Indicators */}
                {result.indicators?.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {result.indicators.slice(0, 3).map((indicator, idx) => (
                      <li key={idx} className="text-sm">• {indicator}</li>
                    ))}
                    {result.indicators.length > 3 && (
                      <li className="text-sm text-gray-500">+{result.indicators.length - 3} more indicators</li>
                    )}
                  </ul>
                )}
                
                {/* Recommendations */}
                {result.recommendations && (
                  <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                    <p className="font-medium text-sm mb-1">Recommended actions:</p>
                    <ul className="text-sm space-y-1">
                      {result.recommendations.map((rec, idx) => (
                        <li key={idx}>✓ {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Job Posting Analyzer */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Analyze Job Posting</h3>
        <p className="text-gray-600 mb-4 text-sm">
          Paste job details to check for fraud indicators (salary scams, fake companies, etc.)
        </p>
        
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            placeholder="Job Title *"
            value={jobData.title}
            onChange={(e) => setJobData({...jobData, title: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-xl text-sm"
          />
          <input
            type="text"
            placeholder="Company Name"
            value={jobData.company}
            onChange={(e) => setJobData({...jobData, company: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-xl text-sm"
          />
          <input
            type="text"
            placeholder="Salary (e.g., £50,000/year)"
            value={jobData.salary}
            onChange={(e) => setJobData({...jobData, salary: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-xl text-sm"
          />
          <input
            type="email"
            placeholder="Contact Email"
            value={jobData.contact_email}
            onChange={(e) => setJobData({...jobData, contact_email: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-xl text-sm"
          />
        </div>
        
        <textarea
          placeholder="Job Description *"
          value={jobData.description}
          onChange={(e) => setJobData({...jobData, description: e.target.value})}
          rows={3}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm mb-4"
        />
        
        <button
          onClick={analyzeJob}
          disabled={analyzingJob}
          className={`w-full py-3 rounded-xl font-semibold text-white transition-colors ${
            analyzingJob
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-orange-500 hover:bg-orange-600'
          }`}
        >
          {analyzingJob ? 'Analyzing...' : 'Analyze Job Posting'}
        </button>

        {/* Job Analysis Result */}
        {jobResult && (
          <div className={`mt-6 rounded-xl border-2 p-4 ${
            jobResult.is_suspicious 
              ? 'from-red-100 to-orange-100 border-red-300' 
              : 'from-green-100 to-emerald-100 border-green-300'
          }`}>
            <h4 className="font-semibold mb-2">
              {jobResult.is_suspicious ? '⚠️ Suspicious Job Posting' : '✅ Job Appears Legitimate'}
            </h4>
            <p className="text-sm mb-3">Risk Level: <strong>{jobResult.risk_level}</strong></p>
            
            {jobResult.red_flags?.length > 0 && (
              <div className="mb-3">
                <p className="font-medium text-red-700 text-sm">Red Flags:</p>
                <ul className="text-sm text-red-600 space-y-1">
                  {jobResult.red_flags.map((flag, idx) => (
                    <li key={idx}>• {flag}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {jobResult.green_flags?.length > 0 && (
              <div className="mb-3">
                <p className="font-medium text-green-700 text-sm">Positive Signs:</p>
                <ul className="text-sm text-green-600 space-y-1">
                  {jobResult.green_flags.map((flag, idx) => (
                    <li key={idx}>• {flag}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {jobResult.recommendations && (
              <div>
                <p className="font-medium text-sm">Recommendations:</p>
                <ul className="text-sm space-y-1">
                  {jobResult.recommendations.map((rec, idx) => (
                    <li key={idx}>✓ {rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Resources Section */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">📚 Helpful Resources</h3>
        <div className="grid md:grid-cols-2 gap-3">
          <a 
            href="https://www.actionfraud.police.uk" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl">🇬🇧</span>
            <div>
              <p className="font-medium text-sm">Action Fraud UK</p>
              <p className="text-xs text-gray-600">Report cyber crime</p>
            </div>
          </a>
          <a 
            href="https://www.ncsc.gov.uk/phishing" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl">🛡️</span>
            <div>
              <p className="font-medium text-sm">NCSC Guidance</p>
              <p className="text-xs text-gray-600">Official phishing advice</p>
            </div>
          </a>
          <a 
            href="https://www.virustotal.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl">🔍</span>
            <div>
              <p className="font-medium text-sm">VirusTotal</p>
              <p className="text-xs text-gray-600">Analyze suspicious URLs</p>
            </div>
          </a>
          <a 
            href="mailto:report@phishing.gov.uk"
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-xl">📧</span>
            <div>
              <p className="font-medium text-sm">Report Phishing</p>
              <p className="text-xs text-gray-600">report@phishing.gov.uk</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}

export default SecurityPanel;