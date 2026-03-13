/**
 * Sidebar Component
 * Side navigation with quick actions
 */
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, FolderPlus, Upload, Trash2 } from 'lucide-react';

const Sidebar = ({ isOpen, onClose, onUploadClick, onCreateFolderClick }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isTrash = location.pathname === '/trash';
  const isDashboard = location.pathname === '/dashboard';

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-4 space-y-2">
          <button
            onClick={onUploadClick}
            className="w-full flex items-center space-x-3 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            <Upload className="w-5 h-5" />
            <span>Upload Files</span>
          </button>

          <button
            onClick={onCreateFolderClick}
            className="w-full flex items-center space-x-3 px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
          >
            <FolderPlus className="w-5 h-5" />
            <span>New Folder</span>
          </button>
        </div>

        <div className="px-4 py-2 mt-4">
          <div
            onClick={() => { navigate('/dashboard'); onClose(); }}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg cursor-pointer transition ${
              isDashboard
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            <Home className="w-5 h-5" />
            <span>My Files</span>
          </div>
          <div
            onClick={() => { navigate('/trash'); onClose(); }}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg cursor-pointer transition ${
              isTrash
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
          >
            <Trash2 className="w-5 h-5" />
            <span>Recycle Bin</span>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
