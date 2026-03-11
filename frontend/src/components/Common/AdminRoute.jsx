/**
 * AdminRoute Component
 * Protects routes that require the ADMIN role.
 * Redirects to /dashboard if the user is not an admin.
 */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

const AdminRoute = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" />;
  if (user?.role !== 'ADMIN') return <Navigate to="/dashboard" />;

  return children;
};

export default AdminRoute;
