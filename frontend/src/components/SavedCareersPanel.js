import React, { useEffect, useState } from 'react';
import api from '../api/api';
import { toast } from 'react-hot-toast';

function SavedCareersPanel() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const response = await api.getFavorites();
        if (response.success) {
          setFavorites(response.favorites || []);
        }
      } catch (error) {
        console.error('Failed to load favorites:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, []);

  const handleRemove = async (role) => {
    try {
      await api.removeFavorite(role);
      setFavorites((current) => current.filter((favorite) => favorite.role !== role));
      const savedJobs = JSON.parse(localStorage.getItem('savedCareers') || '[]');
      localStorage.setItem(
        'savedCareers',
        JSON.stringify(savedJobs.filter((favorite) => favorite.role !== role))
      );
      toast.success('Saved career removed');
    } catch (error) {
      toast.error(error.message || 'Failed to remove saved career');
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">Saved Careers</h3>
        <span className="text-sm text-gray-500">{favorites.length} saved</span>
      </div>

      {loading ? (
        <p className="text-sm text-gray-500">Loading saved careers...</p>
      ) : favorites.length === 0 ? (
        <p className="text-sm text-gray-500">
          Save a few recommendations to build a stronger dashboard history for your dissertation demo.
        </p>
      ) : (
        <div className="space-y-3">
          {favorites.slice(0, 6).map((favorite) => (
            <div key={favorite.role} className="rounded-xl border border-gray-200 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{favorite.role}</h4>
                  <p className="text-sm text-gray-600">{favorite.description}</p>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    <span className="px-2 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                      {favorite.match_score || 0}% match
                    </span>
                    {favorite.salary_range && (
                      <span className="px-2 py-1 rounded-full bg-green-50 text-green-700 border border-green-200">
                        {favorite.salary_range}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleRemove(favorite.role)}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SavedCareersPanel;
