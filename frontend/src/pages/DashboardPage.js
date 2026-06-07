/**
 * Dashboard Page
 * Shows user profile and quick links
 <AnalyticsDashboard />
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import SavedCareersPanel from '../components/SavedCareersPanel';


function DashboardPage() {
  const { user } = useAuth();

  if (!user) return <div>Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome, {user.full_name}!</h1>
        <p className="text-gray-600 mb-8">Here is your career development dashboard.</p>
        
        <div className="grid md:grid-cols-2 gap-6">
          {/* Quick Action: Get Recommendations */}
          <Link to="/" className="block p-6 border-2 border-blue-100 rounded-xl hover:bg-blue-50 transition-colors">
            <h3 className="text-xl font-bold text-blue-700 mb-2">🎯 Get Recommendations</h3>
            <p className="text-gray-600 text-sm">Find AI-driven career paths based on your skills.</p>
          </Link>

          {/* Quick Action: Security Check */}
          <Link to="/cybersecurity" className="block p-6 border-2 border-orange-100 rounded-xl hover:bg-orange-50 transition-colors">
            <h3 className="text-xl font-bold text-orange-700 mb-2">🔐 Security Center</h3>
            <p className="text-gray-600 text-sm">Check URLs and job postings for safety.</p>
          </Link>
        </div>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">Your Profile</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">Email:</span> {user.email}</div>
            <div><span className="text-gray-500">Industry:</span> {user.industry || 'Technology'}</div>
            <div><span className="text-gray-500">Skills:</span> {user.skills?.join(', ') || 'None added'}</div>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <AnalyticsDashboard />
      </div>

      <div className="mt-8">
        <SavedCareersPanel />
      </div>
    </div>
  );
}

export default DashboardPage;
