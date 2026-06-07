/**
 * AI Career Recommender - API Service Layer
 * Proposal Alignment: Objective 4 - React frontend for user interaction
 * Handles all backend communication with JWT auth, error handling, and feature integration
 * 
 * Features:
 * - Token sanitization to prevent JWT validation errors
 * - FormData support for file uploads
 * - Request timeout and retry logic
 * - Comprehensive error handling
 * - Environment-aware debug logging
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const REQUEST_TIMEOUT = 10000; // 10 seconds
const MAX_RETRIES = 1;

class APIService {
  constructor() {
    this.token = null;
  }

  // ===== Authentication Management =====
  
  /**
   * Store and sanitize JWT token
   * @param {string} token - Raw JWT token from backend
   */
  setToken(token) {
    if (token) {
      // ✅ Sanitize: remove quotes, whitespace, newlines that cause JWT rejection
      const clean = token.toString().trim().replace(/^["']|["']$/g, '').replace(/\s+/g, '');
      this.token = clean;
      localStorage.setItem('access_token', clean);
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`🔐 Token stored: ${clean.substring(0, 30)}...`);
      }
    }
  }

  /**
   * Retrieve and sanitize JWT token
   * @returns {string|null} Cleaned token or null
   */
  getToken() {
    const token = this.token || localStorage.getItem('access_token');
    if (token) {
      // ✅ Sanitize on retrieval too
      return token.toString().trim().replace(/^["']|["']$/g, '').replace(/\s+/g, '');
    }
    return null;
  }

  /**
   * Clear authentication state
   */
  logout() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    if (process.env.NODE_ENV === 'development') {
      console.log('🔐 User logged out, tokens cleared');
    }
  }

  // ===== Core Request Handler =====
  
  /**
   * Make HTTP request to backend API
   * @param {string} endpoint - API endpoint path
   * @param {string} method - HTTP method
   * @param {any} data - Request body data
   * @param {boolean} requireAuth - Whether to include JWT token
   * @param {boolean} isFormData - Whether data is FormData (for file uploads)
   * @param {number} retries - Remaining retry attempts
   * @returns {Promise<any>} API response
   */
  async request(endpoint, method = 'GET', data = null, requireAuth = false, isFormData = false, retries = MAX_RETRIES) {
    const url = `${API_BASE}${endpoint}`;
    const token = this.getToken();
    
    // Build headers
    const headers = {};
    
    // Only set Content-Type for JSON requests (FormData sets its own boundary)
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
      headers['Accept'] = 'application/json';
    }
    
    // Attach sanitized token if auth required
    if (requireAuth && token) {
      const cleanToken = token.toString().trim().replace(/^["']|["']$/g, '').replace(/\s+/g, '');
      headers['Authorization'] = `Bearer ${cleanToken}`;
      
      // Dev-only debug logging
      if (process.env.NODE_ENV === 'development') {
        console.log(`🔐 Sending auth to ${endpoint}: ${cleanToken.substring(0, 30)}...`);
      }
    } else if (requireAuth && !token && process.env.NODE_ENV === 'development') {
      console.warn(`⚠️ Auth required for ${endpoint} but no token found!`);
    }

    // Build fetch config with timeout
    const config = {
      method,
      headers,
      credentials: 'include',
      signal: AbortSignal.timeout(REQUEST_TIMEOUT)
    };

    // Add body if present
    if (data) {
      if (isFormData) {
        config.body = data; // FormData - browser sets Content-Type with boundary
      } else {
        config.body = JSON.stringify(data);
      }
    }

    try {
      if (process.env.NODE_ENV === 'development') {
        console.log(`📡 ${method} ${url}`);
      }
      
      const response = await fetch(url, config);
      
      // Handle network errors (status 0 = no response)
      if (!response.ok && response.status === 0) {
        throw new Error('Cannot connect to backend. Ensure server is running on http://localhost:5000');
      }
      
      // Parse response based on content type
      const contentType = response.headers.get('content-type');
      const result = contentType?.includes('application/json') 
        ? await response.json() 
        : await response.text();
      
      // Handle HTTP errors with detailed messages
      if (!response.ok) {
        const error = {
          status: response.status,
          message: result.error || result.message || 'Request failed',
          ...result
        };
        
        if (process.env.NODE_ENV === 'development') {
          console.error(`❌ API Error ${response.status}:`, error);
        }
        
        throw error;
      }
      
      if (process.env.NODE_ENV === 'development') {
        console.log(`✅ ${method} ${endpoint} | ${response.status}`);
      }
      
      return result;
      
    } catch (error) {
      // Retry logic for network errors
      if (retries > 0 && (error.name === 'TypeError' || error.message?.includes('fetch') || error.message?.includes('timeout'))) {
        if (process.env.NODE_ENV === 'development') {
          console.log(`🔄 Retrying ${endpoint}... (${retries} attempts left)`);
        }
        return this.request(endpoint, method, data, requireAuth, isFormData, retries - 1);
      }
      
      // Handle specific error types
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${REQUEST_TIMEOUT}ms. Please try again.`);
      }
      
      if (error.name === 'TypeError' && error.message?.includes('fetch')) {
        throw new Error('Cannot connect to backend. Ensure server is running on http://localhost:5000');
      }
      
      // Re-throw API errors
      if (error.status) {
        throw error;
      }
      
      // Unknown errors
      console.error('❌ Unexpected error:', error);
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }

  // ===== AUTHENTICATION ENDPOINTS (Proposal: Objective 3) =====
  
  /**
   * Register new user
   * @param {Object} userData - User registration data
   */
  async register(userData) {
    return this.request('/auth/register', 'POST', userData, false);
  }

  /**
   * Login user and store token
   * @param {string} email - User email
   * @param {string} password - User password
   */
  async login(email, password) {
    const result = await this.request('/auth/login', 'POST', { email, password }, false);
    if (result.success && result.access_token) {
      this.setToken(result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
    }
    return result;
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser() {
    return this.request('/auth/me', 'GET', null, true);
  }

  // ===== AI RECOMMENDATION ENDPOINTS (Proposal: Objective 1 - Hybrid) =====
  
  /**
   * Get hybrid career recommendations
   * @param {string[]} skills - User's skills array
   * @param {string} industry - Target industry
   * @param {string} experienceLevel - Experience level
   */
  async getRecommendations(skills, industry = 'Technology', experienceLevel = 'Intermediate') {
    return this.request('/ai/recommend', 'POST', {
      skills,
      industry,
      experience_level: experienceLevel
    }, false); // Auth optional for recommendations
  }

  /**
   * Analyze user skills against career requirements
   * @param {string[]} skills - User's skills array
   */
  async analyzeSkills(skills) {
    return this.request('/ai/skills/analyze', 'POST', { skills }, false);
  }

  /**
   * Submit feedback for collaborative filtering training
   * @param {string} role - Career role
   * @param {number} rating - Rating 1-5
   * @param {string[]} skillsProvided - Skills used for recommendation
   * @param {string} feedbackText - Optional feedback text
   */
  async submitFeedback(role, rating, skillsProvided = [], feedbackText = '') {
    return this.request('/ai/feedback', 'POST', {
      role,
      rating,
      skills_provided: skillsProvided,
      feedback_text: feedbackText
    }, true);
  }

  async getFavorites() {
    return this.request('/ai/favorites', 'GET', null, true);
  }

  async saveFavorite(favorite) {
    return this.request('/ai/favorites', 'POST', favorite, true);
  }

  async removeFavorite(role) {
    return this.request(`/ai/favorites/${encodeURIComponent(role)}`, 'DELETE', null, true);
  }

  /**
   * Log user interaction with recommendation
   * @param {string} role - Career role
   * @param {string} interactionType - Type: view, favorite, click, rate
   * @param {number|null} rating - Optional rating
   */
  async logInteraction(role, interactionType = 'view', rating = null) {
    return this.request(`/ai/recommendations/${encodeURIComponent(role)}/interact`, 'POST', {
      type: interactionType,
      rating
    }, true);
  }

  // ===== RESUME PARSING ENDPOINT (Proposal: Objective 3 Enhancement) =====
  
  /**
   * Parse uploaded resume/CV and extract skills
   * @param {File} file - Resume file (PDF/DOCX/TXT)
   */
  async parseResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    // ✅ Pass isFormData=true so Content-Type isn't overridden
    return this.request('/resume/parse', 'POST', formData, false, true);
  }

  // ===== CYBERSECURITY ENDPOINTS (Proposal: Objectives 2, 5) =====
  
  /**
   * Get contextual cybersecurity tips
   * @param {string} category - Tip category: job_search, phishing_awareness, data_privacy
   */
  async getSecurityTips(category = 'job_search') {
    return this.request(`/cybersecurity/tips?category=${category}`, 'GET', null, false);
  }

  /**
   * Check if a URL is potentially malicious
   * @param {string} url - URL to check
   */
  async checkUrlSafety(url) {
    return this.request('/cybersecurity/check-url', 'POST', { url }, false);
  }

  /**
   * Analyze job posting content for fraud indicators
   * @param {Object} jobData - Job posting data
   */
  async analyzeJobPosting(jobData) {
    return this.request('/cybersecurity/analyze-job', 'POST', jobData, false);
  }

  // ===== EVALUATION ENDPOINTS (Proposal: Objective 6) =====
  
  /**
   * Get recommendation accuracy metrics for a user
   * @param {number} userId - User ID
   * @param {number} days - Time period in days
   */
  async getUserAccuracy(userId, days = 30) {
    return this.request(`/evaluation/accuracy/${userId}?days=${days}`, 'GET', null, true);
  }

  /**
   * Get cybersecurity feature engagement stats
   * @param {number|null} userId - Optional user ID filter
   * @param {number} days - Time period in days
   */
  async getSecurityEngagement(userId = null, days = 30) {
    const params = new URLSearchParams({ days });
    if (userId) params.append('user_id', userId);
    return this.request(`/evaluation/security-engagement?${params}`, 'GET', null, true);
  }

  // ===== SYSTEM ENDPOINTS =====
  
  /**
   * Get system health status
   */
  async getHealth() {
    return this.request('/health', 'GET', null, false);
  }

  /**
   * Get API system information
   */
  async getSystemInfo() {
    return this.request('/', 'GET', null, false);
  }
}

// Singleton instance for consistent API access
export const api = new APIService();
export default api;
