/**
 * FileList Component
 * Displays files and folders in a grid view with multi-selection support.
 * Selection state is managed by the parent (Dashboard).
 */
import React, { useState } from 'react';
import {
  File,
  Folder,
  FileText,
  Image,
  Music,
  Video,
  Archive,
  Edit,
  Check,
} from 'lucide-react';
import fileService from '../../services/fileService';

const FileList = ({ files, selectedIds, onToggleSelect, onFileClick, onRefresh }) => {
  const [hoveredId, setHoveredId] = useState(null);
  const [renamingFile, setRenamingFile] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  const getFileIcon = (file) => {
    if (file.is_folder) {
      return <Folder className="w-10 h-10 text-yellow-400" />;
    }
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
  };

  const handleCardClick = (file) => {
    if (selectedIds.size > 0) {
      onToggleSelect(file.id);
    } else if (file.is_folder) {
      onFileClick(file);
    }
  };

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

  return (
    <>
      {/* File grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        {files.map((file) => {
          const isSelected = selectedIds.has(file.id);
          const isHovered = hoveredId === file.id;
          const showCheckbox = isHovered || isSelected || selectedIds.size > 0;

          return (
            <div
              key={file.id}
              className={`relative rounded-xl p-3 cursor-pointer transition-all select-none
                ${isSelected
                  ? 'bg-blue-50 border-2 border-blue-400 shadow-sm'
                  : 'bg-white border-2 border-transparent hover:border-gray-200 hover:shadow-md'
                }`}
              onClick={() => handleCardClick(file)}
              onMouseEnter={() => setHoveredId(file.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              {/* Checkbox */}
              <div
                className={`absolute top-2 left-2 z-10 transition-opacity ${showCheckbox ? 'opacity-100' : 'opacity-0'}`}
                onClick={(e) => { e.stopPropagation(); onToggleSelect(file.id); }}
              >
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors
                  ${isSelected
                    ? 'bg-blue-500 border-blue-500'
                    : 'bg-white border-gray-400 hover:border-blue-400'
                  }`}
                >
                  {isSelected && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                </div>
              </div>

              {/* Rename button (hover, not selected) */}
              {isHovered && !isSelected && (
                <button
                  className="absolute top-2 right-2 z-10 p-1 bg-white rounded-md shadow-sm hover:bg-gray-100 transition"
                  onClick={(e) => startRename(e, file)}
                  title="Rename"
                >
                  <Edit className="w-3.5 h-3.5 text-gray-500" />
                </button>
              )}

              {/* Icon */}
              <div className="flex justify-center mb-3 mt-2">
                {getFileIcon(file)}
              </div>

              {/* Name */}
              {renamingFile?.id === file.id ? (
                <input
                  autoFocus
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  onBlur={confirmRename}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') confirmRename();
                    if (e.key === 'Escape') setRenamingFile(null);
                  }}
                  onClick={(e) => e.stopPropagation()}
                  className="w-full text-xs text-center border border-blue-400 rounded px-1 py-0.5 outline-none"
                />
              ) : (
                <p className="text-xs font-medium text-gray-800 truncate text-center" title={file.file_name}>
                  {file.file_name}
                </p>
              )}

              {/* Meta */}
              <p className="text-xs text-gray-400 text-center mt-1">
                {file.is_folder ? 'Folder' : fileService.formatFileSize(file.file_size)}
              </p>
            </div>
          );
        })}
      </div>

      {files.length === 0 && (
        <div className="text-center py-16">
          <Folder className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No files yet</h3>
          <p className="text-gray-500">Upload your first file to get started</p>
        </div>
      )}
    </>
  );
};

export default FileList;
