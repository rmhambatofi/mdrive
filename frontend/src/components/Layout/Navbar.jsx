/**
 * Navbar Component
 * Top navigation bar with user menu
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LogOut, User, Cloud, Menu, ShieldCheck, UserCog } from 'lucide-react';
import { Link } from 'react-router-dom';
import ThemeToggle from '../Common/ThemeToggle';

const Navbar = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const formatStorage = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1000) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1024 ** 2 * 1000) return `${(bytes / 1024 ** 2).toFixed(2)} MB`;
    if (bytes < 1024 ** 3 * 1000) return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
    return `${(bytes / (1024 ** 3 * 1000)).toFixed(2)} TB`;
  };

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
        >
          <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        </button>

        <div className="flex items-center space-x-2">
          <Cloud className="w-8 h-8 text-blue-600" />
          <span className="text-xl font-bold text-gray-900 dark:text-white">MDrive</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {user && (
          <div className="hidden md:flex flex-col space-y-1 min-w-36">
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>{formatStorage(user.storage_used)} / {formatStorage(user.storage_quota)}</span>
              <span className={`font-medium ${
                user.storage_used / user.storage_quota >= 0.9 ? 'text-red-500' :
                user.storage_used / user.storage_quota >= 0.7 ? 'text-orange-500' :
                'text-gray-500 dark:text-gray-400'
              }`}>
                {((user.storage_used / user.storage_quota) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  user.storage_used / user.storage_quota >= 0.9 ? 'bg-red-500' :
                  user.storage_used / user.storage_quota >= 0.7 ? 'bg-orange-400' :
                  'bg-blue-500'
                }`}
                style={{ width: `${Math.min((user.storage_used / user.storage_quota) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}

        <ThemeToggle />

        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <span className="hidden md:block text-sm font-medium text-gray-700 dark:text-gray-300">
              {user?.full_name || user?.email}
            </span>
          </button>

          {showUserMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowUserMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-20">
                <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{user?.full_name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                </div>

                {user?.role === 'ADMIN' && (
                  <Link
                    to="/admin"
                    onClick={() => setShowUserMenu(false)}
                    className="w-full px-4 py-3 text-left text-sm text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/40 flex items-center space-x-2 transition"
                  >
                    <ShieldCheck className="w-4 h-4" />
                    <span>Administration</span>
                  </Link>
                )}

                <Link
                  to="/profile"
                  onClick={() => setShowUserMenu(false)}
                  className="w-full px-4 py-3 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 flex items-center space-x-2 transition"
                >
                  <UserCog className="w-4 h-4" />
                  <span>My profile</span>
                </Link>

                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 flex items-center space-x-2 transition"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign out</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
