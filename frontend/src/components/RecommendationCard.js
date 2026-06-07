import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';
import { toast } from 'react-hot-toast';

function RecommendationCard({ recommendation, onFeedback }) {
  const { isAuthenticated } = useAuth();
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const savedJobs = JSON.parse(localStorage.getItem('savedCareers') || '[]');
    setSaved(savedJobs.some((career) => career.role === recommendation.role));
  }, [recommendation.role]);

  const handleSave = async () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to save careers');
      return;
    }

    setSaving(true);
    try {
      await api.saveFavorite({
        role: recommendation.role,
        match_score: recommendation.match_score,
        skills_needed: recommendation.missing_skills || [],
        description: recommendation.description,
        salary_range: recommendation.salary_range,
        growth_outlook: recommendation.growth_outlook
      });

      const savedJobs = JSON.parse(localStorage.getItem('savedCareers') || '[]');
      if (!savedJobs.find((career) => career.role === recommendation.role)) {
        savedJobs.push({
          role: recommendation.role,
          industry: recommendation.industry,
          match_score: recommendation.match_score,
          saved_at: new Date().toISOString()
        });
        localStorage.setItem('savedCareers', JSON.stringify(savedJobs));
      }

      setSaved(true);
      toast.success(`Saved "${recommendation.role}"`);
    } catch (error) {
      toast.error(error.message || 'Failed to save career');
    } finally {
      setSaving(false);
    }
  };

  const handleLearnMore = () => {
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(
      `${recommendation.role} career UK salary requirements`
    )}`;
    window.open(searchUrl, '_blank', 'noopener,noreferrer');
  };

  const handleFeedback = async (rating) => {
    if (!isAuthenticated) {
      toast.error('Please sign in to provide feedback');
      return;
    }

    try {
      await api.submitFeedback(
        recommendation.role,
        rating,
        recommendation.matched_skills || [],
        `Rated ${rating}/5`
      );
      toast.success('Thank you for your feedback');
      if (onFeedback) onFeedback(recommendation.role, rating);
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800 border-green-200';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-blue-100 text-blue-800 border-blue-200';
  };

  const missingSkills = recommendation.missing_skills || [];
  const matchedSkills = recommendation.matched_skills || [];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-all">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="text-lg font-bold text-gray-900">{recommendation.role}</h3>
            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
              {recommendation.industry || 'Technology'}
            </span>
            {recommendation.cold_start && (
              <span className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full">
                cold-start safe
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">{recommendation.description}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-bold border ${getScoreColor(recommendation.match_score)}`}>
          {recommendation.match_score}% Match
        </span>
      </div>

      <div className="mb-4 grid md:grid-cols-2 gap-3">
        <div className="rounded-xl bg-green-50 border border-green-100 p-3">
          <h4 className="text-sm font-semibold text-green-900 mb-2">Matched Skills</h4>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.slice(0, 4).map((skill, idx) => (
              <span key={idx} className="px-2.5 py-1 rounded-full text-xs bg-green-100 text-green-800 border border-green-200">
                {skill}
              </span>
            ))}
            {matchedSkills.length === 0 && (
              <span className="text-xs text-green-700">Broad semantic match</span>
            )}
          </div>
        </div>

        <div className="rounded-xl bg-blue-50 border border-blue-100 p-3">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Skills to Develop</h4>
          <div className="flex flex-wrap gap-2">
            {missingSkills.slice(0, 4).map((skill, idx) => (
              <span key={idx} className="px-2.5 py-1 rounded-full text-xs bg-blue-100 text-blue-700 border border-blue-200">
                {skill}
              </span>
            ))}
            {missingSkills.length === 0 && (
              <span className="px-2.5 py-1 rounded-full text-xs bg-green-50 text-green-700 border border-green-200">
                Strong skill alignment
              </span>
            )}
          </div>
        </div>
      </div>

      {recommendation.fallback_reason && (
        <div className="mb-4 rounded-xl bg-amber-50 border border-amber-200 p-3 text-sm text-amber-800">
          {recommendation.fallback_reason}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 text-sm mb-4">
        <div>
          <span className="font-medium text-gray-700">Salary:</span>
          <p className="text-green-600 font-semibold">{recommendation.salary_range}</p>
        </div>
        <div>
          <span className="font-medium text-gray-700">Growth:</span>
          <p className="text-green-600 font-semibold">{recommendation.growth_outlook}</p>
        </div>
      </div>

      <div className="flex gap-2 pt-4 border-t">
        <button
          onClick={handleSave}
          disabled={saved || saving}
          className={`flex-1 py-2 px-3 rounded-lg font-medium text-sm ${
            saved ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
          }`}
        >
          {saved ? 'Saved' : saving ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={handleLearnMore}
          className="flex-1 py-2 px-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 text-sm"
        >
          Learn More
        </button>
      </div>

      {isAuthenticated && (
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-gray-600 mb-2">Rate this recommendation:</p>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button key={star} onClick={() => handleFeedback(star)} className="text-xl hover:scale-110">
                ★
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default RecommendationCard;
