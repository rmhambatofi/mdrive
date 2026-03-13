/**
 * FileList Component
 * Orchestrator that delegates rendering to TilesView, ListView, or CompactListView.
 */
import React, { useState } from 'react';
import FolderIcon from '../Common/FolderIcon';
import fileService from '../../services/fileService';
import useResizableColumns from '../../hooks/useResizableColumns';
import TilesView from './TilesView';
import ListView from './ListView';
import CompactListView from './CompactListView';

const FileList = ({ files, selectedIds, onToggleSelect, onFileClick, onRefresh, viewMode = 'tiles' }) => {
  const [hoveredId, setHoveredId] = useState(null);
  const [renamingFile, setRenamingFile] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  const { widths: listWidths, handleMouseDown: listMouseDown } = useResizableColumns('mdrive_list_cols', [160, 100]);
  const { widths: compactWidths, handleMouseDown: compactMouseDown } = useResizableColumns('mdrive_compact_cols', [160, 100]);

  const startRename = (e, file) => {
    e.stopPropagation();
    setRenamingFile(file);
    setRenameValue(file.file_name);
  };

  const confirmRename = async () => {
    if (renameValue && renameValue !== renamingFile.file_name) {
      try {
        await fileService.renameFile(renamingFile.id, renameValue);
        onRefresh();
      } catch {
        alert('Failed to rename file');
      }
    }
    setRenamingFile(null);
  };

  if (files.length === 0) {
    return (
      <div className="text-center py-16">
        <FolderIcon className="w-16 h-16 mx-auto mb-4 opacity-30" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No files yet</h3>
        <p className="text-gray-500 dark:text-gray-400">Upload your first file to get started</p>
      </div>
    );
  }

  const sharedProps = {
    files,
    selectedIds,
    hoveredId,
    renamingFile,
    renameValue,
    onToggleSelect,
    onFileClick,
    onHover: setHoveredId,
    onStartRename: startRename,
    onRenameChange: (e) => setRenameValue(e.target.value),
    onConfirmRename: confirmRename,
    onCancelRename: () => setRenamingFile(null),
  };

  if (viewMode === 'list') return <ListView {...sharedProps} columnWidths={listWidths} onColumnResize={listMouseDown} />;
  if (viewMode === 'compact') return <CompactListView {...sharedProps} columnWidths={compactWidths} onColumnResize={compactMouseDown} />;
  return <TilesView {...sharedProps} />;
};

export default FileList;
