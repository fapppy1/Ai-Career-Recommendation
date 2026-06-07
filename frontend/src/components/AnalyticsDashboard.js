/**
 * Analytics Dashboard Component
 * Proposal Alignment: Objective 6 - Evaluation through testing
 * Displays recommendation accuracy, user engagement, and performance metrics
 */

import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { useAuth } from '../context/AuthContext';
import api from '../api/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function AnalyticsDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [securityEngagement, setSecurityEngagement] = useState(null);

  useEffect(() => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    const fetchMetrics = async () => {
      try {
        const [accuracyRes, securityRes] = await Promise.all([
          api.getUserAccuracy(user.id, 30),
          api.getSecurityEngagement(user.id, 30)
        ]);

        if (accuracyRes.success) setMetrics(accuracyRes.data);
        if (securityRes.success) setSecurityEngagement(securityRes.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const ratingDistribution = metrics?.rating_distribution || {};
  const precisionPct = metrics ? (metrics.precision * 100).toFixed(1) : '0.0';

  const ratingData = {
    labels: ['5★', '4★', '3★', '2★', '1★'],
    datasets: [{
      label: 'Your Ratings',
      data: [
        ratingDistribution['5_star'] || 0,
        ratingDistribution['4_star'] || 0,
        ratingDistribution['3_star'] || 0,
        ratingDistribution['2_star'] || 0,
        ratingDistribution['1_star'] || 0,
      ],
      backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#6B7280'],
      borderRadius: 4,
    }]
  };

  const engagementData = {
    labels: ['URL Checks', 'Feedback'],
    datasets: [{
      label: 'Feature Usage',
      data: [
        securityEngagement?.total_url_checks || 0,
        metrics?.total_feedback || 0
      ],
      backgroundColor: ['#8B5CF6', '#14B8A6'],
      borderRadius: 4,
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'bottom' },
      title: { display: true, font: { size: 14 } }
    },
    scales: {
      y: { beginAtZero: true, ticks: { stepSize: 1 } }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Your Analytics</h2>
        <button
          onClick={() => {
            const csv = `Metric,Value\nAverage Rating,${metrics?.average_rating || 0}\nPrecision,${metrics?.precision || 0}\nTotal Feedback,${metrics?.total_feedback || 0}`;
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics_user_${user?.id}.csv`;
            a.click();
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Export for Dissertation
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow border border-gray-100">
          <p className="text-sm text-gray-600">Average Rating</p>
          <p className="text-2xl font-bold text-green-600">{metrics?.average_rating || 0}/5.0</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow border border-gray-100">
          <p className="text-sm text-gray-600">Precision@6</p>
          <p className="text-2xl font-bold text-blue-600">{precisionPct}%</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow border border-gray-100">
          <p className="text-sm text-gray-600">Total Feedback</p>
          <p className="text-2xl font-bold text-purple-600">{metrics?.total_feedback || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow border border-gray-100">
          <p className="text-sm text-gray-600">URL Checks</p>
          <p className="text-2xl font-bold text-orange-600">{securityEngagement?.total_url_checks || 0}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Rating Distribution</h3>
          <Bar data={ratingData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, title: { display: false } } }} />
        </div>
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Feature Usage</h3>
          <Bar data={engagementData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, title: { display: false } } }} />
        </div>
      </div>

      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
        <p className="text-sm text-blue-800">
          <strong>Proposal Alignment (Objective 6):</strong> These metrics support a more defensible dissertation evaluation by using recorded user feedback and security-tool usage instead of placeholder values.
        </p>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;
