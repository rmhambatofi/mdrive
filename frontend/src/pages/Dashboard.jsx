/**
 * Dashboard Page
 * Main file management interface
 */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Layout/Navbar';
import Sidebar from '../components/Layout/Sidebar';
import FileList from '../components/FileManager/FileList';
import FileUpload from '../components/FileManager/FileUpload';
import CreateFolderModal from '../components/Common/CreateFolderModal';
import ConfirmModal from '../components/Common/ConfirmModal';
import Breadcrumb from '../components/Common/Breadcrumb';
import ViewModeSelector from '../components/Common/ViewModeSelector';
import SortSelector, { sortFiles } from '../components/Common/SortSelector';
import fileService from '../services/fileService';
import { Loader2, Download, Trash2, X, UploadCloud, CheckCircle2, XCircle } from 'lucide-react';

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

  // View mode (persisted in localStorage)
  const [viewMode, setViewMode] = useState(() => localStorage.getItem('mdrive_view_mode') || 'tiles');
  const handleViewModeChange = (mode) => { setViewMode(mode); localStorage.setItem('mdrive_view_mode', mode); };

  // Sort state (persisted in localStorage)
  const [sortField, setSortField] = useState(() => localStorage.getItem('mdrive_sort_field') || 'name');
  const [sortDirection, setSortDirection] = useState(() => localStorage.getItem('mdrive_sort_dir') || 'asc');
  const handleSortChange = ({ field, direction }) => {
    setSortField(field); setSortDirection(direction);
    localStorage.setItem('mdrive_sort_field', field);
    localStorage.setItem('mdrive_sort_dir', direction);
  };

  // Drag & drop state
  const dragCounter = useRef(0);
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const [dropQueue, setDropQueue] = useState([]); // [{ name, status: 'uploading'|'done'|'error', error }]

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

  // ── Drag & drop handlers ──────────────────────────────────────────────────
  const handleDragEnter = (e) => {
    e.preventDefault();
    dragCounter.current += 1;
    if (dragCounter.current === 1) setIsDraggingOver(true);
  };

  const handleDragOver = (e) => {
    e.preventDefault(); // required to allow drop
  };

  const handleDragLeave = () => {
    dragCounter.current -= 1;
    if (dragCounter.current === 0) setIsDraggingOver(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    dragCounter.current = 0;
    setIsDraggingOver(false);

    // Use DataTransferItemList to filter out directories
    const droppedFiles = Array.from(e.dataTransfer.items)
      .filter((item) => item.kind === 'file' && item.webkitGetAsEntry?.()?.isFile !== false)
      .map((item) => item.getAsFile())
      .filter(Boolean);

    if (droppedFiles.length === 0) return;

    const initialQueue = droppedFiles.map((f) => ({ name: f.name, status: 'uploading' }));
    setDropQueue(initialQueue);

    let hasChanges = false;
    for (let i = 0; i < droppedFiles.length; i++) {
      try {
        await fileService.uploadFile(droppedFiles[i], currentFolderId);
        hasChanges = true;
        setDropQueue((prev) =>
          prev.map((item, idx) => (idx === i ? { ...item, status: 'done' } : item))
        );
      } catch (err) {
        const msg = err.response?.data?.error || 'Upload failed';
        setDropQueue((prev) =>
          prev.map((item, idx) => (idx === i ? { ...item, status: 'error', error: msg } : item))
        );
      }
    }

    if (hasChanges) {
      await refreshUser();
      loadFiles();
    }

    setTimeout(() => setDropQueue([]), 4000);
  };

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

        <main
          className="flex-1 p-6 lg:p-8 relative"
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* Drop overlay */}
          {isDraggingOver && (
            <div className="absolute inset-0 z-40 m-2 rounded-2xl border-2 border-dashed border-blue-400 bg-blue-50/90 dark:bg-blue-950/90 flex flex-col items-center justify-center pointer-events-none">
              <UploadCloud className="w-14 h-14 text-blue-500 mb-3" />
              <p className="text-lg font-semibold text-blue-600 dark:text-blue-300">Drop files to upload</p>
              <p className="text-sm text-blue-500 dark:text-blue-400 mt-1">
                {currentFolderId ? 'Into current folder' : 'Into root folder'}
              </p>
            </div>
          )}

          <div className="max-w-7xl mx-auto">

            {/* Selection toolbar — full width bar overlaying the title row, no layout shift */}
            <div className="relative mb-6">

              {/* Title + breadcrumb (hidden when selection active) */}
              <div className={`transition-opacity duration-150 ${hasSelection ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
                <div className="flex items-center justify-between mb-2">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Files</h1>
                  <div className="flex items-center space-x-1">
                    <SortSelector sortField={sortField} sortDirection={sortDirection} onChange={handleSortChange} />
                    <ViewModeSelector value={viewMode} onChange={handleViewModeChange} />
                  </div>
                </div>
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
                files={sortFiles(files, sortField, sortDirection)}
                selectedIds={selectedIds}
                onToggleSelect={toggleSelect}
                onFileClick={handleFolderClick}
                onRefresh={loadFiles}
                viewMode={viewMode}
              />
            )}
          </div>

          {/* Drop upload status panel */}
          {dropQueue.length > 0 && (
            <div className="absolute bottom-6 right-6 z-50 w-72 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-xl overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                <span className="text-sm font-semibold text-gray-900 dark:text-white">Uploading files</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {dropQueue.filter((f) => f.status === 'done').length}/{dropQueue.length} done
                </span>
              </div>
              <ul className="max-h-48 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
                {dropQueue.map((item, i) => (
                  <li key={i} className="flex items-center space-x-3 px-4 py-2.5">
                    {item.status === 'uploading' && (
                      <Loader2 className="w-4 h-4 text-blue-500 animate-spin flex-shrink-0" />
                    )}
                    {item.status === 'done' && (
                      <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                    )}
                    {item.status === 'error' && (
                      <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">{item.name}</p>
                      {item.status === 'error' && (
                        <p className="text-xs text-red-500 truncate">{item.error}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
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
        message={`Move ${selectedIds.size} item(s) to Recycle Bin?`}
        confirmLabel="Delete"
        variant="danger"
        loading={deleting}
      />
    </div>
  );
};

export default Dashboard;
