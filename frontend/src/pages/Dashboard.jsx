/**
 * Dashboard Page
 * Main file management interface
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Layout/Navbar';
import Sidebar from '../components/Layout/Sidebar';
import FileList from '../components/FileManager/FileList';
import FileUpload from '../components/FileManager/FileUpload';
import CreateFolderModal from '../components/Common/CreateFolderModal';
import Breadcrumb from '../components/Common/Breadcrumb';
import fileService from '../services/fileService';
import { Loader2 } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [files, setFiles] = useState([]);
  const [breadcrumb, setBreadcrumb] = useState([]);
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [createFolderModalOpen, setCreateFolderModalOpen] = useState(false);

  useEffect(() => {
    loadFiles();
  }, [currentFolderId]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const data = await fileService.getFiles(currentFolderId);
      setFiles(data.files || []);
      setBreadcrumb(data.breadcrumb || []);
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFolderClick = (folder) => {
    setCurrentFolderId(folder.id);
  };

  const handleBreadcrumbNavigate = (folderId) => {
    setCurrentFolderId(folderId);
  };

  const handleUploadComplete = () => {
    loadFiles();
  };

  const handleFolderCreated = () => {
    loadFiles();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onUploadClick={() => {
            setUploadModalOpen(true);
            setSidebarOpen(false);
          }}
          onCreateFolderClick={() => {
            setCreateFolderModalOpen(true);
            setSidebarOpen(false);
          }}
        />

        <main className="flex-1 p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">My Files</h1>
              <Breadcrumb
                items={breadcrumb}
                onNavigate={handleBreadcrumbNavigate}
              />
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            ) : (
              <FileList
                files={files}
                onFileClick={handleFolderClick}
                onRefresh={loadFiles}
              />
            )}
          </div>
        </main>
      </div>

      <FileUpload
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
        currentFolderId={currentFolderId}
      />

      <CreateFolderModal
        isOpen={createFolderModalOpen}
        onClose={() => setCreateFolderModalOpen(false)}
        onFolderCreated={handleFolderCreated}
        currentFolderId={currentFolderId}
      />
    </div>
  );
};

export default Dashboard;
