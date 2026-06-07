/**
 * Explainability Modal - "Why this recommendation?"
 * Proposal Alignment: Objective 7 - Reflection on AI accuracy and user trust
 * Provides transparent reasoning for hybrid recommendations
 */

import React from 'react';

function ExplainabilityModal({ isOpen, onClose, recommendation, userSkills }) {
  if (!isOpen) return null;

  const userSkillsLower = (userSkills || []).map(s => s.toLowerCase());
  const requiredSkills = recommendation.required_skills || recommendation.skills_needed || [];
  
  const matched = requiredSkills.filter(s => userSkillsLower.includes(s.toLowerCase()));
  const missing = requiredSkills.filter(s => !userSkillsLower.includes(s.toLowerCase()));

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                Why "{recommendation.role}"?
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Algorithm: {recommendation.algorithm?.replace('_', ' ') || 'Content-based'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              &times;
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Match Summary */}
          <div className="bg-blue-50 rounded-xl p-4">
            <h4 className="font-semibold text-blue-900 mb-2">Skill Match Summary</h4>
            <p className="text-blue-800">
              You have <strong>{matched.length}</strong> of <strong>{requiredSkills.length}</strong> required skills.
              {missing.length > 0 && ` Consider developing ${missing.length} additional skills to strengthen your fit.`}
            </p>
          </div>

          {/* Matched Skills */}
          {matched.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">✅ Your Matching Skills</h4>
              <div className="flex flex-wrap gap-2">
                {matched.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Missing Skills */}
          {missing.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">🎯 Skills to Develop</h4>
              <div className="flex flex-wrap gap-2">
                {missing.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Algorithm Explanation */}
          <div className="bg-purple-50 rounded-xl p-4">
            <h4 className="font-semibold text-purple-900 mb-2">How This Was Calculated</h4>
            {recommendation.algorithm === 'hybrid_cf' ? (
              <p className="text-purple-800 text-sm">
                This recommendation combines:
                <br />• <strong>70% Content-based</strong>: Your skills match {recommendation.content_score}% of requirements
                <br />• <strong>30% Collaborative</strong>: Users with similar profiles rated this role highly ({recommendation.cf_score}%)
                <br />• <strong>Final Score</strong>: Weighted average = {recommendation.hybrid_score}%
              </p>
            ) : (
              <p className="text-purple-800 text-sm">
                This recommendation is based on content-based filtering:
                <br />• Your skills were compared to career requirements using cosine similarity
                <br />• Match score: {recommendation.content_score || recommendation.match_score}%
                <br />• Adjusted for your experience level: {recommendation.experience_fit || 'Intermediate'}
              </p>
            )}
          </div>

          {/* Salary & Growth Explanation */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-xl p-4">
              <h4 className="font-semibold text-green-900 mb-2">💰 Salary Alignment</h4>
              <p className="text-green-800 text-sm">
                Based on your skill match, you could target the <strong>{recommendation.salary_range}</strong> range.
                Developing missing skills may help you reach the higher end.
              </p>
            </div>
            <div className="bg-blue-50 rounded-xl p-4">
              <h4 className="font-semibold text-blue-900 mb-2">📈 Growth Outlook</h4>
              <p className="text-blue-800 text-sm">
                This role has <strong>{recommendation.growth_outlook}</strong> demand, 
                making it a strategic choice for long-term career development.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Got it, thanks!
          </button>
        </div>
      </div>
    </div>
  );
}

export default ExplainabilityModal;