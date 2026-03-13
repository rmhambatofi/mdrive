import React from 'react';
import { Edit } from 'lucide-react';
import FileCheckbox from './FileCheckbox';
import FileRenameInput from './FileRenameInput';
import { getFileIcon, formatDate } from './fileIconUtils';
import fileService from '../../services/fileService';

const CompactListView = ({
  files,
  selectedIds,
  hoveredId,
  renamingFile,
  renameValue,
  columnWidths,
  onColumnResize,
  onToggleSelect,
  onFileClick,
  onHover,
  onStartRename,
  onRenameChange,
  onConfirmRename,
  onCancelRename,
}) => {
  const gridCols = `32px 1fr ${columnWidths[0]}px ${columnWidths[1]}px`;

  const handleClick = (file) => {
    if (selectedIds.size > 0) onToggleSelect(file.id);
    else if (file.is_folder) onFileClick(file);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div
        className="items-center px-4 py-1 border-b border-gray-100 dark:border-gray-700 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
        style={{ display: 'grid', gridTemplateColumns: gridCols }}
      >
        <div />
        <div className="pl-7 px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-default">Name</div>
        <div className="relative px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-default">
          <div className="absolute -left-1 top-0 bottom-0 w-2 cursor-col-resize z-10 group" onMouseDown={(e) => onColumnResize(0, e)}>
            <div className="mx-auto w-px h-full group-hover:bg-blue-400 group-active:bg-blue-500" />
          </div>
          Modified
        </div>
        <div className="text-right relative px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-default">
          <div className="absolute -left-1 top-0 bottom-0 w-2 cursor-col-resize z-10 group" onMouseDown={(e) => onColumnResize(1, e)}>
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
          <div
            key={file.id}
            className={`items-center px-4 py-1.5 cursor-pointer transition-colors select-none border-b border-gray-50 dark:border-gray-700/50
              ${isSelected
                ? 'bg-blue-50 dark:bg-blue-900/30'
                : 'hover:bg-gray-50 dark:hover:bg-gray-800/60'
              }`}
            style={{ display: 'grid', gridTemplateColumns: gridCols }}
            onClick={() => handleClick(file)}
            onMouseEnter={() => onHover(file.id)}
            onMouseLeave={() => onHover(null)}
          >
            <div className="w-8 flex-shrink-0">
              <FileCheckbox isSelected={isSelected} visible={showCb} onToggle={() => onToggleSelect(file.id)} />
            </div>

            <div className="flex items-center space-x-2 min-w-0">
              <div className="flex-shrink-0">
                {getFileIcon(file, 'sm')}
              </div>
              <div className="min-w-0 flex-1 flex items-center space-x-2">
                {renamingFile?.id === file.id ? (
                  <FileRenameInput
                    value={renameValue}
                    onChange={onRenameChange}
                    onConfirm={onConfirmRename}
                    onCancel={onCancelRename}
                  />
                ) : (
                  <span className="text-sm text-gray-800 dark:text-gray-200 truncate" title={file.file_name}>
                    {file.file_name}
                  </span>
                )}
                {isHovered && !isSelected && (
                  <button
                    className="flex-shrink-0 p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                    onClick={(e) => onStartRename(e, file)}
                    title="Rename"
                  >
                    <Edit className="w-3 h-3 text-gray-400" />
                  </button>
                )}
              </div>
            </div>

            <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {formatDate(file.updated_at)}
            </div>

            <div className="text-xs text-gray-500 dark:text-gray-400 text-right">
              {file.is_folder ? '' : fileService.formatFileSize(file.file_size)}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CompactListView;
