/**
 * Sidebar Component
 * Side navigation with quick actions
 */
import React from 'react';
import { Home, FolderPlus, Upload } from 'lucide-react';

const Sidebar = ({ isOpen, onClose, onUploadClick, onCreateFolderClick }) => {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ${
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
            className="w-full flex items-center space-x-3 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            <FolderPlus className="w-5 h-5" />
            <span>New Folder</span>
          </button>
        </div>

        <div className="px-4 py-2 mt-4">
          <div className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg cursor-pointer transition">
            <Home className="w-5 h-5" />
            <span>My Files</span>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
