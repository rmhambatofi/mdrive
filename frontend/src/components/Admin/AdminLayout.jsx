/**
 * AdminLayout
 * Shared layout for all admin pages: full-width Navbar + left sidebar + content area.
 */
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Users, Settings, ChevronLeft, ShieldCheck } from 'lucide-react';
import Navbar from '../Layout/Navbar';

const NAV_ITEMS = [
  {
    to: '/admin/users',
    icon: Users,
    label: 'Manage Users',
  },
  {
    to: '/admin/settings',
    icon: Settings,
    label: 'Settings',
  },
];

const AdminLayout = ({ children, title, subtitle }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar onMenuClick={() => {}} />

      <div className="flex max-w-7xl mx-auto px-4 py-8 gap-6">
        {/* Sidebar */}
        <aside className="w-56 flex-shrink-0">
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden sticky top-8">
            {/* Sidebar header */}
            <div className="px-4 py-4 border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition mb-3"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Dashboard</span>
              </button>
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-purple-600 dark:text-purple-400">
                  Administration
                </span>
              </div>
            </div>

            {/* Nav items */}
            <nav className="py-2">
              {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-4 py-2.5 text-sm transition ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 font-medium'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{label}</span>
                </NavLink>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {(title || subtitle) && (
            <div className="mb-6">
              {title && (
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h1>
              )}
              {subtitle && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{subtitle}</p>
              )}
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
