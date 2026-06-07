/**
 * Home Page - Main Career Recommendation Interface
 * Proposal Alignment: Objectives 1, 3, 4 - AI recommendations with user interaction
 * Integrates: Hybrid recommendations, resume parsing, skill analysis, cybersecurity
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';
import { toast } from 'react-hot-toast';

// Components
import RecommendationCard from '../components/RecommendationCard';
import ResumeUpload from '../components/ResumeUpload';
import SecurityPanel from '../components/SecurityPanel';

function HomePage() {
  const { user, isAuthenticated } = useAuth();
  
  // Form state
  const [industry, setIndustry] = useState('Technology');
  const [skills, setSkills] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('Intermediate');
  const [loading, setLoading] = useState(false);
  const [showResumeModal, setShowResumeModal] = useState(false);
  
  // Results state
  const [recommendations, setRecommendations] = useState([]);
  const [skillAnalysis, setSkillAnalysis] = useState(null);
  const [metadata, setMetadata] = useState(null);
  
  // Security state
  const [showSecurityPanel, setShowSecurityPanel] = useState(false);

  // ===== Input Validation =====
  const validateSkills = (input) => {
    if (!input || !input.trim()) {
      return { valid: false, error: 'Please enter at least one skill' };
    }
    
    // Limit to 20 skills
    const skillsArray = input.split(',').map(s => s.trim()).filter(s => s);
    if (skillsArray.length > 20) {
      return { valid: false, error: 'Maximum 20 skills allowed' };
    }
    
    // Limit each skill to 50 chars
    if (skillsArray.some(s => s.length > 50)) {
      return { valid: false, error: 'Each skill must be under 50 characters' };
    }
    
    // Remove duplicates
    const unique = [...new Set(skillsArray.map(s => s.toLowerCase()))];
    if (unique.length !== skillsArray.length) {
      toast('Removed duplicate skills');
    }
    
    return { valid: true, skills: skillsArray };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validation = validateSkills(skills);
    if (!validation.valid) {
      toast.error(validation.error);
      return;
    }

    setLoading(true);
    setRecommendations([]);
    setSkillAnalysis(null);

    try {
      const response = await api.getRecommendations(
        validation.skills,
        industry,
        experienceLevel
      );

      if (response.success) {
        setRecommendations(response.recommendations);
        setSkillAnalysis(response.skill_analysis);
        setMetadata(response.metadata);
        toast.success(`Found ${response.recommendations.length} career paths!`);
      } else {
        toast.error(response.error || 'Failed to get recommendations');
      }
    } catch (error) {
      toast.error(error.message || 'Network error - please try again');
    } finally {
      setLoading(false);
    }
  };

  const handleResumeParsed = (parsedData) => {
    if (parsedData.all_skills_flat?.length > 0) {
      setSkills(parsedData.all_skills_flat.join(', '));
      toast.success(`Extracted ${parsedData.all_skills_flat.length} skills from your resume!`);
    }
    
    if (parsedData.estimated_experience_years) {
      const years = parsedData.estimated_experience_years;
      if (years < 2) setExperienceLevel('Beginner');
      else if (years < 5) setExperienceLevel('Intermediate');
      else if (years < 8) setExperienceLevel('Advanced');
      else setExperienceLevel('Expert');
    }
    
    setShowResumeModal(false);
  };

  const handleFeedback = async (role, rating) => {
    if (!isAuthenticated) {
      toast.error('Please login to submit feedback');
      return;
    }
    
    try {
      await api.submitFeedback(role, rating, skills.split(',').map(s => s.trim()));
      toast.success('Thank you for your feedback!');
      // Refresh recommendations to incorporate feedback
      if (recommendations.length > 0) {
        handleSubmit(new Event('submit'));
      }
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      {/* ===== HERO SECTION ===== */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
          Discover Your{' '}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI Career Path
          </span>
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Powered by hybrid AI algorithms and cybersecurity awareness to protect your future.
        </p>
      </div>

      {/* ===== QUICK SECURITY BANNER ===== */}
      <div 
        className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl p-4 mb-8 cursor-pointer hover:shadow-md transition-shadow flex items-center justify-between"
        onClick={() => setShowSecurityPanel(!showSecurityPanel)}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">🔐</span>
          <div>
            <h3 className="font-semibold text-gray-900">Cybersecurity Tip</h3>
            <p className="text-gray-700 text-sm">Always verify job postings on official company sites</p>
          </div>
        </div>
        <span className="text-blue-600 font-medium text-sm flex items-center gap-1">
          {showSecurityPanel ? 'Hide Panel' : 'Show Security Tools'} 
          <span className={`transition-transform duration-200 ${showSecurityPanel ? '-rotate-90' : 'rotate-0'}`}>→</span>
        </span>
      </div>

      {/* ===== COLLAPSIBLE SECURITY PANEL ===== */}
      {showSecurityPanel && (
        <div className="mb-8 animate-fade-in">
          <SecurityPanel />
        </div>
      )}

      {/* ===== MAIN CONTENT GRID ===== */}
      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* ----- LEFT COLUMN: Form & Results ----- */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Career Input Form */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Tell Us About Your Skills</h2>
              {isAuthenticated && (
                <button
                  onClick={() => setShowResumeModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:opacity-90 transition-all text-sm font-medium shadow-md"
                >
                  <span>📄</span>
                  <span>Upload Resume</span>
                </button>
              )}
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Industry Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Target Industry
                </label>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  aria-label="Select target industry"
                >
                  <option value="Technology">Technology</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Finance">Finance</option>
                  <option value="Education">Education</option>
                  <option value="E-commerce">E-commerce</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Skills Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Skills (comma-separated)
                </label>
                <div className="relative">
                  <textarea
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                    placeholder="e.g., Python, Machine Learning, SQL, Data Analysis"
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition resize-none"
                    aria-label="Enter your skills separated by commas"
                    maxLength={1000}
                  />
                  <span className="absolute bottom-3 right-3 text-xs text-gray-400">
                    {skills.length}/1000
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Tip: Use commas to separate skills (max 20 skills)
                </p>
              </div>

              {/* Experience Level */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Experience Level
                </label>
                <div className="flex flex-wrap gap-2">
                  {['Beginner', 'Intermediate', 'Advanced', 'Expert'].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setExperienceLevel(level)}
                      className={`px-4 py-2 rounded-lg transition-all text-sm font-medium ${
                        experienceLevel === level
                          ? 'bg-blue-600 text-white shadow-md scale-105'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:scale-105'
                      }`}
                      aria-pressed={experienceLevel === level}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full py-4 px-6 rounded-xl font-bold text-white transition-all shadow-lg ${
                  loading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:shadow-xl hover:scale-[1.02]'
                }`}
                aria-busy={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
                    Analyzing with Hybrid AI...
                  </span>
                ) : (
                  '🚀 Get AI Career Recommendations'
                )}
              </button>
            </form>

            {/* Demo Button for Non-Authenticated Users */}
            {!isAuthenticated && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => {
                    setSkills('Python, Machine Learning, SQL');
                    setIndustry('Technology');
                    setExperienceLevel('Intermediate');
                    toast('Demo skills loaded! Sign in to save your profile.');
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 underline font-medium"
                >
                  Try demo recommendations (no sign-in required)
                </button>
              </div>
            )}
          </div>

          {/* ===== LOADING SKELETON ===== */}
          {loading && (
            <div className="space-y-4">
              <div className="h-6 bg-gray-200 rounded animate-pulse w-1/3"></div>
              {metadata?.fallback_note && (
                <div className="mb-4 rounded-xl bg-amber-50 border border-amber-200 p-4 text-sm text-amber-800">
                  {metadata.fallback_note}
                </div>
              )}
              <div className="grid md:grid-cols-2 gap-6">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                    <div className="h-6 bg-gray-200 rounded animate-pulse w-3/4 mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3 mb-4"></div>
                    <div className="flex gap-2">
                      <div className="h-8 bg-gray-200 rounded animate-pulse w-20"></div>
                      <div className="h-8 bg-gray-200 rounded animate-pulse w-20"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skill Analysis Results */}
          {skillAnalysis && !loading && (
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 animate-fade-in">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                📊 Your Skill Analysis
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {Object.entries(skillAnalysis).map(([category, data]) => (
                  category !== 'overall' && data.matched_skills?.length > 0 && (
                    <div key={category} className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition">
                      <h4 className="font-semibold text-gray-900 mb-2">{category}</h4>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">Coverage:</span>
                        <span className="text-sm font-bold text-blue-600">{data.coverage_pct}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all" 
                          style={{ width: `${data.coverage_pct}%` }}
                        ></div>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {data.matched_skills.map((skill, i) => (
                          <span 
                            key={i}
                            className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                      {data.suggested_additions?.length > 0 && (
                        <p className="text-xs text-gray-500 mt-2">
                          💡 Consider: {data.suggested_additions.join(', ')}
                        </p>
                      )}
                    </div>
                  )
                ))}
              </div>
              
              {/* Overall Summary */}
              {skillAnalysis.overall && (
                <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <p className="text-sm text-blue-800">
                    <strong>Overall Match:</strong> You have {skillAnalysis.overall.relevant_to_careers} of {skillAnalysis.overall.skills_provided} skills that match AI career requirements.
                    {skillAnalysis.overall.top_missing?.length > 0 && (
                      <> <br/>🎯 Top skills to develop: {skillAnalysis.overall.top_missing.slice(0, 3).join(', ')}.</>
                    )}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Recommendations Grid */}
          {recommendations.length > 0 && !loading && (
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  🎯 Recommended Career Paths
                </h2>
                {metadata && (
                  <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full font-medium">
                    {metadata.algorithm.replace('_', ' ')} • {metadata.weights.content}/{metadata.weights.collaborative}
                  </span>
                )}
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {recommendations.map((rec, index) => (
                  <RecommendationCard 
                    key={index} 
                    recommendation={rec} 
                    onFeedback={handleFeedback}
                    showExplainability={true}
                  />
                ))}
              </div>
            </div>
          )}

          {/* ===== ERROR BOUNDARY ===== */}
          {!loading && recommendations.length === 0 && skillAnalysis && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-center">
              <p className="text-amber-800 font-semibold">We found skill matches but no final recommendations</p>
              <p className="text-amber-700 text-sm mt-2">
                Try a broader industry selection or fewer filters, then run the recommendation again.
              </p>
            </div>
          )}
        </div>

        {/* ----- RIGHT COLUMN: Sidebar ----- */}
        <div className="space-y-6">
          
          {/* User Profile Card */}
          {isAuthenticated && user && (
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-md">
                  <span className="text-white font-bold text-lg">
                    {user.full_name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{user.full_name}</h3>
                  <p className="text-sm text-gray-600">{user.email}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-600">Industry:</span>
                  <span className="font-medium text-gray-900">{user.industry}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-600">Experience:</span>
                  <span className="font-medium text-gray-900">{user.experience_level}</span>
                </div>
                {user.skills?.length > 0 && (
                  <div className="py-1">
                    <span className="text-gray-600 block mb-1">Skills:</span>
                    <div className="flex flex-wrap gap-1">
                      {user.skills.slice(0, 3).map((skill, i) => (
                        <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                          {skill}
                        </span>
                      ))}
                      {user.skills.length > 3 && (
                        <span className="text-xs text-gray-500">+{user.skills.length - 3} more</span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Why Hybrid AI? Info Card */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              🤖 Why Hybrid AI?
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-2 p-2 rounded-lg bg-blue-50">
                <span className="text-blue-500 text-lg">•</span>
                <p><strong className="text-gray-900">Content-based (70%)</strong>: Matches your skills to career requirements using cosine similarity</p>
              </div>
              <div className="flex items-start gap-2 p-2 rounded-lg bg-purple-50">
                <span className="text-purple-500 text-lg">•</span>
                <p><strong className="text-gray-900">Collaborative (30%)</strong>: Learns from users with similar profiles to improve recommendations</p>
              </div>
              <div className="flex items-start gap-2 p-2 rounded-lg bg-green-50">
                <span className="text-green-500 text-lg">•</span>
                <p><strong className="text-gray-900">Cold-start handling</strong>: Automatically falls back to content-based for new users</p>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4 pt-3 border-t border-gray-100">
              📚 Proposal Alignment: Objective 1 - Advanced recommendation algorithms research
            </p>
          </div>

          {/* Quick Security Tips Card */}
          <div className="bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">🔐</span>
              <h3 className="font-bold text-gray-900">Stay Safe Online</h3>
            </div>
            <ul className="space-y-3 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-orange-500 font-bold">✓</span>
                <span>Verify job postings on official company sites</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-500 font-bold">✓</span>
                <span>Never share NI/bank details in initial applications</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-500 font-bold">✓</span>
                <span>Use our URL checker for suspicious links</span>
              </li>
            </ul>
            <button
              onClick={() => {
                setShowSecurityPanel(true);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              className="mt-5 w-full py-2.5 px-4 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-bold shadow-md"
            >
              Open Security Tools →
            </button>
          </div>

        </div>
      </div>

      {/* ===== EMPTY STATE ===== */}
      {!loading && recommendations.length === 0 && !skillAnalysis && (
        <div className="text-center py-16 bg-gray-50 rounded-2xl mt-8">
          <div className="text-6xl mb-4 animate-bounce">🎯</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Ready to Discover Your Path?
          </h3>
          <p className="text-gray-600 max-w-md mx-auto mb-4">
            Enter your skills above to get personalized AI-powered career recommendations tailored to your experience and goals.
          </p>
          <p className="text-sm text-gray-500 bg-white px-4 py-2 rounded-full inline-flex items-center gap-2 shadow-sm">
            💡 Tip: Upload your resume to auto-fill your skills!
          </p>
        </div>
      )}

      {/* ===== RESUME UPLOAD MODAL ===== */}
      {showResumeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <ResumeUpload
              onParsed={handleResumeParsed}
              onClose={() => setShowResumeModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;
