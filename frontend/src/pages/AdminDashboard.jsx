/**
 * AdminDashboard Page
 * Administration interface — visible to ADMIN role only.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, ShieldCheck, Star, User, Loader2, ChevronLeft } from 'lucide-react';
import Navbar from '../components/Layout/Navbar';
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
  if (bytes >= 1024 ** 3) return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
  if (bytes >= 1024 ** 2) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
};

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
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
    setUpdatingId(userUuid);
    try {
      const data = await adminService.updateUserRole(userUuid, newRole);
      setUsers((prev) => prev.map((u) => (u.id === userUuid ? data.user : u)));
    } catch {
      setError('Failed to update role.');
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar onMenuClick={() => {}} />

      <main className="max-w-7xl mx-auto px-4 py-8">

        {/* Header */}
        <div className="flex items-center space-x-4 mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-lg transition"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Administration</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">Manage users and roles</p>
          </div>
        </div>

        {/* Stats cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard icon={Users} label="Total Users" value={stats.total} color="blue" />
            <StatCard icon={ShieldCheck} label="Admins" value={stats.admins} color="purple" />
            <StatCard icon={Star} label="Subscribers" value={stats.subscribers} color="green" />
            <StatCard icon={User} label="Limited" value={stats.limited_subscribers} color="gray" />
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
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Storage</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Joined</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Change role</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900 dark:text-gray-100">{user.full_name || '—'}</div>
                        <div className="text-gray-500 dark:text-gray-400 text-xs">{user.email}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_CLASSES[user.role]}`}>
                          {ROLE_LABELS[user.role] ?? user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                        {formatStorage(user.storage_used)} / {formatStorage(user.storage_quota)}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="px-6 py-4">
                        <select
                          value={user.role}
                          disabled={updatingId === user.id}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
                        >
                          {ROLES.map((r) => (
                            <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                          ))}
                        </select>
                        {updatingId === user.id && (
                          <Loader2 className="inline w-4 h-4 ml-2 text-blue-600 animate-spin" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color }) => {
  const colors = {
    blue:   'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
    green:  'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    gray:   'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400',
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
