/**
 * Admin service
 * API calls for administration operations (ADMIN role only)
 */
import api from './api';

const adminService = {
  /**
   * Fetch all users with summary statistics.
   * @returns {{ users: Array, stats: object }}
   */
  getUsers: async () => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  /**
   * Update a user's role.
   * @param {string} userUuid
   * @param {string} role  - 'ADMIN' | 'SUBSCRIBER' | 'LIMITED_SUBSCRIBER'
   */
  updateUserRole: async (userUuid, role) => {
    const response = await api.put(`/admin/users/${userUuid}/role`, { role });
    return response.data;
  },
};

export default adminService;
