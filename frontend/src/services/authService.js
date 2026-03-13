/**
 * Authentication service
 * Handles user authentication operations
 */
import api from './api';

const authService = {
  /**
   * Register a new user
   */
  register: async (email, password, fullName) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  /**
   * Login user
   */
  login: async (email, password) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  /**
   * Get current user from localStorage
   */
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (e) {
        return null;
      }
    }
    return null;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  /**
   * Get user profile
   */
  getProfile: async () => {
    const response = await api.get('/auth/profile');
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  /**
   * Update user profile
   */
  updateProfile: async (fullName) => {
    const response = await api.put('/auth/profile', {
      full_name: fullName,
    });
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  /**
   * Change user password
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.put('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

export default authService;
