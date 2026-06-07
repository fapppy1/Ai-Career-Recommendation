/**
 * Cybersecurity Page - URL safety checker + security tips
 * Proposal Alignment: Objectives 2, 5 - Phishing detection + awareness
 */

import React, { useState, useEffect } from 'react';
import api from '../api/api';
import { toast } from 'react-hot-toast';

function CybersecurityPage() {
  // URL checker state
  const [urlInput, setUrlInput] = useState('');
  const [checkingUrl, setCheckingUrl] = useState(false);
  const [urlResult, setUrlResult] = useState(null);
  
  // Job analyzer state
  const [jobData, setJobData] = useState({
    title: '',
    company: '',
    description: '',
    salary: '',
    contact_email: ''
  });
  const [analyzingJob, setAnalyzingJob] = useState(false);
  const [jobResult, setJobResult] = useState(null);
  
  // Security tips state
  const [tipCategory, setTipCategory] = useState('job_search');
  const [securityTip, setSecurityTip] = useState('');
  const [allTips, setAllTips] = useState([]);

  // Fetch tips on mount and category change
  useEffect(() => {
    fetchTips();
  }, [tipCategory]);

  const fetchTips = async () => {
    try {
      const response = await api.getSecurityTips(tipCategory);
      if (response.success) {
        setSecurityTip(response.tip);
        setAllTips(response.all_tips);
      }
    } catch (error) {
      console.error('Failed to fetch tips:', error);
    }
  };

  const checkUrl = async () => {
    if (!urlInput.trim()) {
      toast.error('Please enter a URL to check');
      return;
    }

    setCheckingUrl(true);
    setUrlResult(null);

    try {
      const response = await api.checkUrlSafety(urlInput);
      if (response.success) {
        setUrlResult(response.result);
        
        // Show contextual toast
        const messages = {
          'critical': '🚨 CRITICAL: Do not click this link!',
          'high': '⚠️ HIGH RISK: Exercise extreme caution',
          'medium': '⚠️ MEDIUM RISK: Verify before proceeding',
          'low': '✅ LOW RISK: URL appears safe',
          'unknown': '❓ Unable to verify - proceed with caution'
        };
        toast(messages[response.result.risk_level] || messages.unknown, {
          duration: 5000,
          style: {
            background: response.result.is_safe ? '#10B981' : '#EF4444',
            color: '#fff'
          }
        });
      }
    } catch (error) {
      toast.error(error.message || 'Failed to check URL');
    } finally {
      setCheckingUrl(false);
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
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🔐 Cybersecurity Awareness
        </h1>
        <p className="text-xl text-gray-600">
          Protect yourself while searching for AI careers online
        </p>
      </div>

      {/* Security Tips Section */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Security Tips</h2>
          <select
            value={tipCategory}
            onChange={(e) => setTipCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="job_search">Job Search</option>
            <option value="phishing_awareness">Phishing</option>
            <option value="data_privacy">Data Privacy</option>
            <option value="url_safety">URL Safety</option>
          </select>
        </div>
        
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 mb-4">
          <p className="text-lg text-gray-800">{securityTip}</p>
        </div>
        
        <button
          onClick={fetchTips}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Get another tip →
        </button>
        
        {/* All Tips List */}
        <div className="mt-6">
          <h4 className="font-semibold text-gray-900 mb-3">All Tips in this Category:</h4>
          <ul className="space-y-2">
            {allTips.map((tip, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-700">
                <span className="text-blue-500">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* URL Safety Checker */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          🔍 Check Job URL Safety
        </h2>
        <p className="text-gray-600 mb-4">
          Paste a job posting URL to check for phishing indicators
        </p>
        
        <div className="flex gap-2 mb-4">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://example-job-site.com/posting"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && checkUrl()}
          />
          <button
            onClick={checkUrl}
            disabled={checkingUrl}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
              checkingUrl
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {checkingUrl ? 'Checking...' : 'Check'}
          </button>
        </div>

        {/* URL Check Result */}
        {urlResult && (
          <div className={`rounded-xl border-2 p-4 ${getRiskColor(urlResult.risk_level)}`}>
            <div className="flex items-start gap-3">
              <span className="text-2xl">{getRiskIcon(urlResult.risk_level)}</span>
              <div className="flex-1">
                <h4 className="font-semibold">{urlResult.message}</h4>
                
                {urlResult.indicators?.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {urlResult.indicators.map((indicator, idx) => (
                      <li key={idx} className="text-sm">• {indicator}</li>
                    ))}
                  </ul>
                )}
                
                {urlResult.recommendations && (
                  <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                    <p className="font-medium mb-1">Recommended actions:</p>
                    <ul className="text-sm space-y-1">
                      {urlResult.recommendations.map((rec, idx) => (
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
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          📋 Analyze Job Posting
        </h2>
        <p className="text-gray-600 mb-4">
          Paste job details to check for fraud indicators
        </p>
        
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            placeholder="Job Title"
            value={jobData.title}
            onChange={(e) => setJobData({...jobData, title: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg"
          />
          <input
            type="text"
            placeholder="Company Name"
            value={jobData.company}
            onChange={(e) => setJobData({...jobData, company: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg"
          />
          <input
            type="text"
            placeholder="Salary (e.g., £50,000/year)"
            value={jobData.salary}
            onChange={(e) => setJobData({...jobData, salary: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg"
          />
          <input
            type="email"
            placeholder="Contact Email"
            value={jobData.contact_email}
            onChange={(e) => setJobData({...jobData, contact_email: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg"
          />
        </div>
        
        <textarea
          placeholder="Job Description"
          value={jobData.description}
          onChange={(e) => setJobData({...jobData, description: e.target.value})}
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4"
        />
        
        <button
          onClick={analyzeJob}
          disabled={analyzingJob}
          className={`w-full py-3 rounded-lg font-semibold text-white transition-colors ${
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
            <p className="text-sm mb-3">Risk Level: {jobResult.risk_level}</p>
            
            {jobResult.red_flags?.length > 0 && (
              <div className="mb-3">
                <p className="font-medium text-red-700">Red Flags:</p>
                <ul className="text-sm text-red-600 space-y-1">
                  {jobResult.red_flags.map((flag, idx) => (
                    <li key={idx}>• {flag}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {jobResult.green_flags?.length > 0 && (
              <div className="mb-3">
                <p className="font-medium text-green-700">Positive Signs:</p>
                <ul className="text-sm text-green-600 space-y-1">
                  {jobResult.green_flags.map((flag, idx) => (
                    <li key={idx}>• {flag}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {jobResult.recommendations && (
              <div>
                <p className="font-medium">Recommendations:</p>
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
      <div className="mt-8 bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📚 Helpful Resources</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <a 
            href="https://www.actionfraud.police.uk" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-2xl">🇬🇧</span>
            <div>
              <p className="font-semibold">Action Fraud UK</p>
              <p className="text-sm text-gray-600">Report cyber crime and fraud</p>
            </div>
          </a>
          <a 
            href="https://www.ncsc.gov.uk/phishing" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-2xl">🛡️</span>
            <div>
              <p className="font-semibold">NCSC Phishing Guidance</p>
              <p className="text-sm text-gray-600">Official UK cybersecurity advice</p>
            </div>
          </a>
          <a 
            href="https://www.virustotal.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-2xl">🔍</span>
            <div>
              <p className="font-semibold">VirusTotal</p>
              <p className="text-sm text-gray-600">Analyze suspicious URLs and files</p>
            </div>
          </a>
          <a 
            href="mailto:report@phishing.gov.uk"
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className="text-2xl">📧</span>
            <div>
              <p className="font-semibold">Report Phishing</p>
              <p className="text-sm text-gray-600">report@phishing.gov.uk</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}

export default CybersecurityPage;
