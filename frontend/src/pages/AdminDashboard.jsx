/**
 * AdminDashboard Page
 * User management interface — visible to ADMIN role only.
 */
import React, { useState, useEffect } from 'react';
import { Users, ShieldCheck, Star, User, Loader2, UserCheck, UserX } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/Admin/AdminLayout';
import adminService from '../services/adminService';

const ROLES = ['ADMIN', 'SUBSCRIBER', 'LIMITED_SUBSCRIBER'];

const ROLE_LABELS = {
  ADMIN: 'Admin',
  SUBSCRIBER: 'Subscriber',
  LIMITED_SUBSCRIBER: 'Limited',
};

const ROLE_CLASSES = {
  ADMIN: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300',
  SUBSCRIBER: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
  LIMITED_SUBSCRIBER: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300',
};

const formatStorage = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1000) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 ** 2 * 1000) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  if (bytes < 1024 ** 3 * 1000) return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
  return `${(bytes / (1024 ** 3 * 1000)).toFixed(1)} TB`;
};

/** Animated toggle switch */
const Toggle = ({ checked, onChange, disabled }) => (
  <button
    type="button"
    role="switch"
    aria-checked={checked}
    onClick={onChange}
    disabled={disabled}
    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none disabled:opacity-40 disabled:cursor-not-allowed ${
      checked ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
    }`}
  >
    <span
      className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform transition-transform duration-200 ${
        checked ? 'translate-x-5' : 'translate-x-0'
      }`}
    />
  </button>
);

const AdminDashboard = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatingRoleId, setUpdatingRoleId] = useState(null);
  const [togglingId, setTogglingId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await adminService.getUsers();
      setUsers(data.users);
      setStats(data.stats);
    } catch {
      setError('Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userUuid, newRole) => {
    setUpdatingRoleId(userUuid);
    try {
      const data = await adminService.updateUserRole(userUuid, newRole);
      setUsers((prev) => prev.map((u) => (u.id === userUuid ? data.user : u)));
    } catch {
      setError('Failed to update role.');
    } finally {
      setUpdatingRoleId(null);
    }
  };

  const handleToggleActive = async (userUuid) => {
    setTogglingId(userUuid);
    try {
      const data = await adminService.toggleUserActive(userUuid);
      setUsers((prev) => prev.map((u) => (u.id === userUuid ? data.user : u)));
    } catch {
      setError('Failed to update user status.');
    } finally {
      setTogglingId(null);
    }
  };

  return (
    <AdminLayout title="Manage Users" subtitle="Manage user accounts and roles">
      {/* Stats cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
          <StatCard icon={Users}      label="Total"       value={stats.total}               color="blue" />
          <StatCard icon={ShieldCheck} label="Admins"     value={stats.admins}              color="purple" />
          <StatCard icon={Star}       label="Subscribers" value={stats.subscribers}         color="green" />
          <StatCard icon={User}       label="Limited"     value={stats.limited_subscribers} color="gray" />
          <StatCard icon={UserCheck}  label="Active"      value={stats.active}              color="teal" />
          <StatCard icon={UserX}      label="Inactive"    value={stats.inactive}            color="red" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">
          {error}
        </div>
      )}

      {/* Users table */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Users</h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 dark:bg-gray-800 text-left">
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Storage</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Joined</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Change role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {users.map((user) => {
                  const isSelf = user.id === currentUser?.id;
                  return (
                    <tr
                      key={user.id}
                      className={`transition ${
                        user.is_active
                          ? 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
                          : 'bg-gray-50/60 dark:bg-gray-800/30 opacity-60'
                      }`}
                    >
                      {/* User */}
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900 dark:text-gray-100">
                          {user.full_name || '—'}
                          {isSelf && (
                            <span className="ml-2 text-xs text-blue-500 dark:text-blue-400">(you)</span>
                          )}
                        </div>
                        <div className="text-gray-500 dark:text-gray-400 text-xs">{user.email}</div>
                      </td>

                      {/* Status toggle */}
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <Toggle
                            checked={user.is_active}
                            onChange={() => handleToggleActive(user.id)}
                            disabled={isSelf || togglingId === user.id}
                          />
                          {togglingId === user.id ? (
                            <Loader2 className="w-3.5 h-3.5 text-blue-600 animate-spin" />
                          ) : (
                            <span className={`text-xs font-medium ${
                              user.is_active
                                ? 'text-green-600 dark:text-green-400'
                                : 'text-gray-400 dark:text-gray-500'
                            }`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Role badge */}
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_CLASSES[user.role]}`}>
                          {ROLE_LABELS[user.role] ?? user.role}
                        </span>
                      </td>

                      {/* Storage */}
                      <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                        {formatStorage(user.storage_used)} / {formatStorage(user.storage_quota)}
                      </td>

                      {/* Joined */}
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
                      </td>

                      {/* Change role */}
                      <td className="px-6 py-4">
                        <select
                          value={user.role}
                          disabled={updatingRoleId === user.id || isSelf}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
                        >
                          {ROLES.map((r) => (
                            <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                          ))}
                        </select>
                        {updatingRoleId === user.id && (
                          <Loader2 className="inline w-4 h-4 ml-2 text-blue-600 animate-spin" />
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

const StatCard = ({ icon: Icon, label, value, color }) => {
  const colors = {
    blue:   'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
    green:  'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    gray:   'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400',
    teal:   'bg-teal-50 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400',
    red:    'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400',
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-5 flex items-center space-x-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color]}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      </div>
    </div>
  );
};

export default AdminDashboard;
