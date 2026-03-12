/**
 * Settings service
 * API calls for application settings management (ADMIN role only)
 */
import api from './api';

const settingsService = {
  /**
   * Fetch current application settings.
   * @returns {{ settings: { subscriber_quota: number, limited_subscriber_quota: number, updated_at: string } }}
   */
  getSettings: async () => {
    const response = await api.get('/admin/settings');
    return response.data;
  },

  /**
   * Update application settings.
   * Quota values are in bytes.
   * @param {{ subscriber_quota?: number, limited_subscriber_quota?: number }} data
   */
  updateSettings: async (data) => {
    const response = await api.put('/admin/settings', data);
    return response.data;
  },
};

export default settingsService;
