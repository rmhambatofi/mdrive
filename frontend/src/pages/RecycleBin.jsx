/**
 * RecycleBin Page
 * Displays soft-deleted files with restore / permanent delete actions.
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Layout/Navbar';
import Sidebar from '../components/Layout/Sidebar';
import ConfirmModal from '../components/Common/ConfirmModal';
import FolderIcon from '../components/Common/FolderIcon';
import ViewModeSelector from '../components/Common/ViewModeSelector';
import SortSelector, { sortFiles } from '../components/Common/SortSelector';
import fileService from '../services/fileService';
import useResizableColumns from '../hooks/useResizableColumns';
import {
  File,
  FileText,
  Image,
  Music,
  Video,
  Archive,
  Loader2,
  Trash2,
  RotateCcw,
  Check,
  X,
} from 'lucide-react';

const RecycleBin = () => {
  const { refreshUser } = useAuth();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
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

  const [selectedIds, setSelectedIds] = useState(new Set());
  const [hoveredId, setHoveredId] = useState(null);

  const [restoring, setRestoring] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [emptyConfirmOpen, setEmptyConfirmOpen] = useState(false);

  useEffect(() => {
    loadTrash();
  }, []);

  const loadTrash = async () => {
    setLoading(true);
    try {
      const data = await fileService.getTrash();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Failed to load trash:', error);
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

  // ── Actions ────────────────────────────────────────────

  const handleRestoreSelected = async () => {
    setRestoring(true);
    for (const id of selectedIds) {
      try {
        await fileService.restoreFile(id);
      } catch {}
    }
    setRestoring(false);
    clearSelection();
    await refreshUser();
    loadTrash();
  };

  const handleDeleteSelected = () => setDeleteConfirmOpen(true);

  const confirmPermanentDelete = async () => {
    setDeleting(true);
    for (const id of selectedIds) {
      try {
        await fileService.permanentlyDelete(id);
      } catch {}
    }
    setDeleteConfirmOpen(false);
    setDeleting(false);
    clearSelection();
    await refreshUser();
    loadTrash();
  };

  const handleEmptyTrash = () => setEmptyConfirmOpen(true);

  const confirmEmptyTrash = async () => {
    setDeleting(true);
    try {
      await fileService.emptyTrash();
    } catch {}
    setEmptyConfirmOpen(false);
    setDeleting(false);
    clearSelection();
    await refreshUser();
    loadTrash();
  };

  // ── Helpers ────────────────────────────────────────────

  const getFileIcon = (file, size = 'lg') => {
    if (size === 'lg') {
      if (file.is_folder) return <FolderIcon className="w-20 h-20" />;
      const iconMap = {
        image: <Image className="w-10 h-10 text-green-500" />,
        video: <Video className="w-10 h-10 text-purple-500" />,
        audio: <Music className="w-10 h-10 text-pink-500" />,
        pdf: <FileText className="w-10 h-10 text-red-500" />,
        document: <FileText className="w-10 h-10 text-blue-500" />,
        archive: <Archive className="w-10 h-10 text-yellow-600" />,
        text: <FileText className="w-10 h-10 text-gray-500" />,
      };
      return iconMap[file.icon] || <File className="w-10 h-10 text-gray-500" />;
    }
    if (file.is_folder) return <FolderIcon className="w-5 h-5" />;
    const smallMap = {
      image: <Image className="w-5 h-5 text-green-500" />,
      video: <Video className="w-5 h-5 text-purple-500" />,
      audio: <Music className="w-5 h-5 text-pink-500" />,
      pdf: <FileText className="w-5 h-5 text-red-500" />,
      document: <FileText className="w-5 h-5 text-blue-500" />,
      archive: <Archive className="w-5 h-5 text-yellow-600" />,
      text: <FileText className="w-5 h-5 text-gray-500" />,
    };
    return smallMap[file.icon] || <File className="w-5 h-5 text-gray-500" />;
  };

  const formatDeletedDate = (isoString) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const hasSelection = selectedIds.size > 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex">
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onUploadClick={() => {}}
          onCreateFolderClick={() => {}}
        />

        <main className="flex-1 p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">

            {/* Header row — swapped between title and toolbar */}
            <div className="relative mb-6">

              {/* Title (hidden when selection active) */}
              <div className={`transition-opacity duration-150 ${hasSelection ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
                <div className="flex items-center justify-between">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Recycle Bin</h1>
                  <div className="flex items-center space-x-1">
                    <SortSelector sortField={sortField} sortDirection={sortDirection} onChange={handleSortChange} />
                    <ViewModeSelector value={viewMode} onChange={handleViewModeChange} />
                    {files.length > 0 && (
                      <button
                        onClick={handleEmptyTrash}
                        className="flex items-center space-x-1.5 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Empty Recycle Bin</span>
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Items are permanently deleted after 30 days</p>
              </div>

              {/* Toolbar (overlays when selection active) */}
              <div className={`absolute inset-0 transition-opacity duration-150 ${hasSelection ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
                <div className="h-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm rounded-xl flex items-center px-4 space-x-1">

                  <button
                    onClick={handleRestoreSelected}
                    disabled={restoring}
                    className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-md transition disabled:opacity-50"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>{restoring ? 'Restoring...' : 'Restore'}</span>
                  </button>

                  <button
                    onClick={handleDeleteSelected}
                    disabled={deleting}
                    className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition disabled:opacity-50"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>{deleting ? 'Deleting...' : 'Delete permanently'}</span>
                  </button>

                  <div className="flex-1" />

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

            {/* Content */}
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            ) : files.length === 0 ? (
              <div className="text-center py-16">
                <Trash2 className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Recycle Bin is empty</h3>
                <p className="text-gray-500 dark:text-gray-400">Deleted items will appear here</p>
              </div>
            ) : (
              <TrashFileList files={sortFiles(files, sortField, sortDirection)} selectedIds={selectedIds} hoveredId={hoveredId} toggleSelect={toggleSelect} setHoveredId={setHoveredId} getFileIcon={getFileIcon} formatDeletedDate={formatDeletedDate} viewMode={viewMode} />
            )}
          </div>
        </main>
      </div>

      {/* Permanent delete confirmation */}
      <ConfirmModal
        isOpen={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={confirmPermanentDelete}
        title="Delete permanently"
        message={`Permanently delete ${selectedIds.size} item(s)? This action cannot be undone.`}
        confirmLabel="Delete permanently"
        variant="danger"
        loading={deleting}
      />

      {/* Empty trash confirmation */}
      <ConfirmModal
        isOpen={emptyConfirmOpen}
        onClose={() => setEmptyConfirmOpen(false)}
        onConfirm={confirmEmptyTrash}
        title="Empty Recycle Bin"
        message="Permanently delete all items in the Recycle Bin? This action cannot be undone."
        confirmLabel="Empty Recycle Bin"
        variant="danger"
        loading={deleting}
      />
    </div>
  );
};

// ── TrashFileList sub-component (supports tiles / list / compact) ──────────
const TrashFileList = ({ files, selectedIds, hoveredId, toggleSelect, setHoveredId, getFileIcon, formatDeletedDate, viewMode }) => {
  const { widths: listWidths, handleMouseDown: listMouseDown } = useResizableColumns('mdrive_trash_list_cols', [160, 100]);
  const { widths: compactWidths, handleMouseDown: compactMouseDown } = useResizableColumns('mdrive_trash_compact_cols', [160, 100]);

  const renderCheckbox = (file, isSelected, show) => (
    <div
      className={`transition-opacity ${show ? 'opacity-100' : 'opacity-0'}`}
      onClick={(e) => { e.stopPropagation(); toggleSelect(file.id); }}
    >
      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors cursor-pointer
        ${isSelected ? 'bg-blue-500 border-blue-500' : 'bg-white dark:bg-gray-700 border-gray-400 dark:border-gray-500 hover:border-blue-400'}`}>
        {isSelected && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
      </div>
    </div>
  );

  // Tiles
  if (viewMode === 'tiles') {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        {files.map((file) => {
          const isSelected = selectedIds.has(file.id);
          const isHovered = hoveredId === file.id;
          const showCb = isHovered || isSelected || selectedIds.size > 0;
          return (
            <div key={file.id}
              className={`relative rounded-xl p-3 cursor-pointer transition-all select-none
                ${isSelected ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-400 shadow-sm' : 'bg-white dark:bg-gray-800 border-2 border-transparent hover:border-gray-200 dark:hover:border-gray-600 hover:shadow-md'}`}
              onClick={() => toggleSelect(file.id)}
              onMouseEnter={() => setHoveredId(file.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <div className="absolute top-2 left-2 z-10">{renderCheckbox(file, isSelected, showCb)}</div>
              <div className="flex justify-center mb-3 mt-2 opacity-60">{getFileIcon(file, 'lg')}</div>
              <p className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate text-center" title={file.file_name}>{file.file_name}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-1">Deleted {formatDeletedDate(file.deleted_at)}</p>
            </div>
          );
        })}
      </div>
    );
  }

  // List (large icons) or Compact (small icons)
  const isCompact = viewMode === 'compact';
  const colWidths = isCompact ? compactWidths : listWidths;
  const onMouseDown = isCompact ? compactMouseDown : listMouseDown;
  const gridCols = `32px 1fr ${colWidths[0]}px ${colWidths[1]}px`;
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="items-center px-4 py-1 border-b border-gray-100 dark:border-gray-700 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider" style={{ display: 'grid', gridTemplateColumns: gridCols }}>
        <div />
        <div className={`${isCompact ? 'pl-7' : 'pl-14'} px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-default`}>Name</div>
        <div className="relative px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-default">
          <div className="absolute -left-1 top-0 bottom-0 w-2 cursor-col-resize z-10 group" onMouseDown={(e) => onMouseDown(0, e)}>
            <div className="mx-auto w-px h-full group-hover:bg-blue-400 group-active:bg-blue-500" />
          </div>
          Deleted
        </div>
        <div className="text-right relative px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-default">
          <div className="absolute -left-1 top-0 bottom-0 w-2 cursor-col-resize z-10 group" onMouseDown={(e) => onMouseDown(1, e)}>
            <div className="mx-auto w-px h-full group-hover:bg-blue-400 group-active:bg-blue-500" />
          </div>
          Size
        </div>
      </div>
      {files.map((file) => {
        const isSelected = selectedIds.has(file.id);
        const isHovered = hoveredId === file.id;
        const showCb = isHovered || isSelected || selectedIds.size > 0;
        return (
          <div key={file.id}
            className={`items-center px-4 ${isCompact ? 'py-1.5' : 'py-2'} cursor-pointer transition-colors select-none border-b border-gray-50 dark:border-gray-700/50
              ${isSelected ? 'bg-blue-50 dark:bg-blue-900/30' : 'hover:bg-gray-50 dark:hover:bg-gray-800/60'}`}
            style={{ display: 'grid', gridTemplateColumns: gridCols }}
            onClick={() => toggleSelect(file.id)}
            onMouseEnter={() => setHoveredId(file.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <div className="w-8 flex-shrink-0">{renderCheckbox(file, isSelected, showCb)}</div>
            <div className={`flex items-center ${isCompact ? 'space-x-2' : 'space-x-3'} min-w-0 opacity-60`}>
              <div className="flex-shrink-0">{getFileIcon(file, isCompact ? 'sm' : 'lg')}</div>
              <span className="text-sm text-gray-800 dark:text-gray-200 truncate" title={file.file_name}>{file.file_name}</span>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{formatDeletedDate(file.deleted_at)}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 text-right">{file.is_folder ? '' : fileService.formatFileSize(file.file_size)}</div>
          </div>
        );
      })}
    </div>
  );
};

export default RecycleBin;
