/**
 * Authentication Context - React Context API for global auth state
 * Proposal Alignment: Objective 4 - User interaction and personalization
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing session on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = api.getToken();
      const storedUser = localStorage.getItem('user');
      
      if (token && storedUser) {
        try {
          const response = await api.getCurrentUser();
          if (response.success) {
            setUser(response.user);
            setIsAuthenticated(true);
          } else {
            // Token invalid, clear storage
            api.logout();
          }
        } catch (err) {
          console.error('Auth check failed:', err);
          api.logout();
        }
      }
      setLoading(false);
    };
    
    initializeAuth();
  }, []);

  // Login function
  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const result = await api.login(email, password);
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        return { success: true, user: result.user };
      }
      setError(result.error || 'Login failed');
      return { success: false, error: result.error };
    } catch (err) {
      setError(err.message || 'Network error');
      return { success: false, error: err.message };
    }
  }, []);

  // Register function
  const register = useCallback(async (userData) => {
    setError(null);
    try {
      const result = await api.register(userData);
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        return { success: true, user: result.user };
      }
      setError(result.error || 'Registration failed');
      return { success: false, error: result.error };
    } catch (err) {
      setError(err.message || 'Network error');
      return { success: false, error: err.message };
    }
  }, []);

  // Logout function
  const logout = useCallback(() => {
    api.logout();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  // Update user profile
  const updateUser = useCallback((updatedUser) => {
    setUser(prev => prev ? { ...prev, ...updatedUser } : null);
    if (updatedUser) {
      localStorage.setItem('user', JSON.stringify({ ...user, ...updatedUser }));
    }
  }, [user]);

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    updateUser,
    refreshUser: async () => {
      try {
        const response = await api.getCurrentUser();
        if (response.success) {
          setUser(response.user);
          return true;
        }
        return false;
      } catch {
        return false;
      }
    }
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};