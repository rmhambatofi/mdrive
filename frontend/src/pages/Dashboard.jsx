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
import ConfirmModal from '../components/Common/ConfirmModal';
import Breadcrumb from '../components/Common/Breadcrumb';
import fileService from '../services/fileService';
import { Loader2, Download, Trash2, X } from 'lucide-react';

const Dashboard = () => {
  const { refreshUser } = useAuth();
  const [files, setFiles] = useState([]);
  const [breadcrumb, setBreadcrumb] = useState([]);
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [createFolderModalOpen, setCreateFolderModalOpen] = useState(false);

  // Selection state lives here so the toolbar can render above the title
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [deleting, setDeleting] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // Clear selection when navigating to a different folder
  useEffect(() => {
    setSelectedIds(new Set());
    refreshUser();
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

  const toggleSelect = (fileId) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(fileId)) next.delete(fileId);
      else next.add(fileId);
      return next;
    });
  };

  const clearSelection = () => setSelectedIds(new Set());

  const handleDeleteSelected = () => {
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    setDeleting(true);
    for (const id of selectedIds) {
      try {
        await fileService.deleteFile(id);
      } catch {}
    }
    setDeleteConfirmOpen(false);
    setDeleting(false);
    clearSelection();
    await refreshUser();
    loadFiles();
  };

  const handleDownloadSelected = async () => {
    const selected = files.filter((f) => selectedIds.has(f.id));
    const hasFolder = selected.some((f) => f.is_folder);

    if (selected.length >= 2 || hasFolder) {
      try {
        await fileService.downloadZip(selected.map((f) => f.id));
      } catch {
        alert('Failed to create ZIP archive');
      }
    } else if (selected.length === 1) {
      try {
        await fileService.downloadFile(selected[0].id, selected[0].file_name);
      } catch {
        alert('Failed to download file');
      }
    }
  };

  const handleFolderClick = (folder) => {
    setCurrentFolderId(folder.id);
  };

  const handleBreadcrumbNavigate = (folderId) => {
    setCurrentFolderId(folderId);
  };

  const handleUploadComplete = () => loadFiles();
  const handleFolderCreated = () => loadFiles();

  const hasSelection = selectedIds.size > 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
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

            {/* Selection toolbar — full width bar overlaying the title row, no layout shift */}
            <div className="relative mb-6">

              {/* Title + breadcrumb (hidden when selection active) */}
              <div className={`transition-opacity duration-150 ${hasSelection ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">My Files</h1>
                <Breadcrumb items={breadcrumb} onNavigate={handleBreadcrumbNavigate} />
              </div>

              {/* Toolbar bar — absolutely covers the title area */}
              <div className={`absolute inset-0 transition-opacity duration-150 ${hasSelection ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
                <div className="h-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm rounded-xl flex items-center px-4 space-x-1">

                  {/* Actions */}
                  <button
                    onClick={handleDeleteSelected}
                    disabled={deleting}
                    className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md transition disabled:opacity-50"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>{deleting ? 'Deleting...' : 'Delete'}</span>
                  </button>

                  <button
                    onClick={handleDownloadSelected}
                    className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download{selectedIds.size >= 2 ? ' as ZIP' : ''}</span>
                  </button>

                  {/* Spacer */}
                  <div className="flex-1" />

                  {/* Selection count pill */}
                  <button
                    onClick={clearSelection}
                    className="flex items-center space-x-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full px-3 py-1 transition"
                  >
                    <X className="w-3.5 h-3.5 text-gray-600 dark:text-gray-300" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{selectedIds.size} selected</span>
                  </button>

                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            ) : (
              <FileList
                files={files}
                selectedIds={selectedIds}
                onToggleSelect={toggleSelect}
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

      <ConfirmModal
        isOpen={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={confirmDelete}
        title="Delete items"
        message={`Delete ${selectedIds.size} item(s)? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        loading={deleting}
      />
    </div>
  );
};

export default Dashboard;
