import React from 'react';
import { Edit } from 'lucide-react';
import FileCheckbox from './FileCheckbox';
import FileRenameInput from './FileRenameInput';
import { getFileIcon } from './fileIconUtils';
import fileService from '../../services/fileService';

const TilesView = ({
  files,
  selectedIds,
  hoveredId,
  renamingFile,
  renameValue,
  onToggleSelect,
  onFileClick,
  onHover,
  onStartRename,
  onRenameChange,
  onConfirmRename,
  onCancelRename,
}) => {
  const handleClick = (file) => {
    if (selectedIds.size > 0) onToggleSelect(file.id);
    else if (file.is_folder) onFileClick(file);
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
      {files.map((file) => {
        const isSelected = selectedIds.has(file.id);
        const isHovered = hoveredId === file.id;
        const showCb = isHovered || isSelected || selectedIds.size > 0;

        return (
          <div
            key={file.id}
            className={`relative rounded-xl p-3 cursor-pointer transition-all select-none
              ${isSelected
                ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-400 shadow-sm'
                : 'bg-white dark:bg-gray-800 border-2 border-transparent hover:border-gray-200 dark:hover:border-gray-600 hover:shadow-md'
              }`}
            onClick={() => handleClick(file)}
            onMouseEnter={() => onHover(file.id)}
            onMouseLeave={() => onHover(null)}
          >
            <div className="absolute top-2 left-2 z-10">
              <FileCheckbox isSelected={isSelected} visible={showCb} onToggle={() => onToggleSelect(file.id)} />
            </div>

            {isHovered && !isSelected && (
              <button
                className="absolute top-2 right-2 z-10 p-1 bg-white dark:bg-gray-700 rounded-md shadow-sm hover:bg-gray-100 dark:hover:bg-gray-600 transition"
                onClick={(e) => onStartRename(e, file)}
                title="Rename"
              >
                <Edit className="w-3.5 h-3.5 text-gray-500 dark:text-gray-400" />
              </button>
            )}

            <div className="flex justify-center mb-3 mt-2">
              {getFileIcon(file, 'lg')}
            </div>

            {renamingFile?.id === file.id ? (
              <FileRenameInput
                value={renameValue}
                onChange={onRenameChange}
                onConfirm={onConfirmRename}
                onCancel={onCancelRename}
                centered
              />
            ) : (
              <p className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate text-center" title={file.file_name}>
                {file.file_name}
              </p>
            )}

            <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-1">
              {file.is_folder ? 'Folder' : fileService.formatFileSize(file.file_size)}
            </p>
          </div>
        );
      })}
    </div>
  );
};

export default TilesView;
