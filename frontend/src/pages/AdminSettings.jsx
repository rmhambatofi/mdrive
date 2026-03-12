/**
 * AdminSettings Page
 * Application-wide quota configuration — ADMIN only.
 */
import React, { useState, useEffect } from 'react';
import { Save, Loader2, HardDrive, Info } from 'lucide-react';
import AdminLayout from '../components/Admin/AdminLayout';
import settingsService from '../services/settingsService';

// Conversion helpers
const bytesToGb = (bytes) => parseFloat((bytes / 1024 ** 3).toFixed(2));
const gbToBytes = (gb) => Math.round(parseFloat(gb) * 1024 ** 3);

const QuotaField = ({ label, description, value, onChange, disabled }) => (
  <div className="flex flex-col sm:flex-row sm:items-start gap-4 py-5 border-b border-gray-100 dark:border-gray-800 last:border-0">
    <div className="flex-1">
      <label className="block text-sm font-medium text-gray-900 dark:text-gray-100">
        {label}
      </label>
      <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{description}</p>
    </div>
    <div className="flex items-center space-x-2 sm:w-44">
      <input
        type="number"
        min="0.1"
        step="0.1"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
      />
      <span className="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">GB</span>
    </div>
  </div>
);

const AdminSettings = () => {
  const [adminQuotaGb, setAdminQuotaGb] = useState('');
  const [subscriberQuotaGb, setSubscriberQuotaGb] = useState('');
  const [limitedQuotaGb, setLimitedQuotaGb] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await settingsService.getSettings();
      setAdminQuotaGb(bytesToGb(data.settings.admin_quota));
      setSubscriberQuotaGb(bytesToGb(data.settings.subscriber_quota));
      setLimitedQuotaGb(bytesToGb(data.settings.limited_subscriber_quota));
    } catch {
      setError('Failed to load settings.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    const adminBytes = gbToBytes(adminQuotaGb);
    const subscriberBytes = gbToBytes(subscriberQuotaGb);
    const limitedBytes = gbToBytes(limitedQuotaGb);

    if (isNaN(adminBytes) || adminBytes <= 0) {
      setError('Admin quota must be a positive number.');
      return;
    }
    if (isNaN(subscriberBytes) || subscriberBytes <= 0) {
      setError('Subscriber quota must be a positive number.');
      return;
    }
    if (isNaN(limitedBytes) || limitedBytes <= 0) {
      setError('Limited subscriber quota must be a positive number.');
      return;
    }

    setSaving(true);
    try {
      await settingsService.updateSettings({
        admin_quota: adminBytes,
        subscriber_quota: subscriberBytes,
        limited_subscriber_quota: limitedBytes,
      });
      setSuccessMsg('Settings saved successfully.');
    } catch {
      setError('Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <AdminLayout title="Settings" subtitle="Configure application-wide parameters">
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
        {/* Section header */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center space-x-3">
          <HardDrive className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Storage Quotas</h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
          </div>
        ) : (
          <form onSubmit={handleSave}>
            {/* Info banner */}
            <div className="mx-6 mt-5 flex items-start space-x-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 px-4 py-3 rounded-lg text-xs">
              <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>
                Changes apply immediately to all users. Existing users' effective quota will
                reflect the new value on their next action.
              </span>
            </div>

            {/* Fields */}
            <div className="px-6 mt-4">
              <QuotaField
                label="Admin quota"
                description="Maximum storage for administrators (ADMIN role)."
                value={adminQuotaGb}
                onChange={setAdminQuotaGb}
                disabled={saving}
              />
              <QuotaField
                label="Subscriber quota"
                description="Maximum storage for paying subscribers (SUBSCRIBER role)."
                value={subscriberQuotaGb}
                onChange={setSubscriberQuotaGb}
                disabled={saving}
              />
              <QuotaField
                label="Limited subscriber quota"
                description="Maximum storage for free-tier users (LIMITED_SUBSCRIBER role)."
                value={limitedQuotaGb}
                onChange={setLimitedQuotaGb}
                disabled={saving}
              />
            </div>

            {/* Feedback */}
            {error && (
              <div className="mx-6 mt-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
            {successMsg && (
              <div className="mx-6 mt-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded-lg text-sm">
                {successMsg}
              </div>
            )}

            {/* Actions */}
            <div className="px-6 py-4 mt-2 flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>{saving ? 'Saving…' : 'Save changes'}</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminSettings;
