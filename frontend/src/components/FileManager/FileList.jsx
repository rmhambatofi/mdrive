/**
 * FileList Component
 * Displays files and folders in a list/grid view
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
  MoreVertical,
  Download,
  Trash2,
  Edit,
} from 'lucide-react';
import fileService from '../../services/fileService';

const FileList = ({ files, onFileClick, onRefresh }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const getFileIcon = (file) => {
    if (file.is_folder) {
      return <Folder className="w-8 h-8 text-blue-500" />;
    }

    const iconMap = {
      image: <Image className="w-8 h-8 text-green-500" />,
      video: <Video className="w-8 h-8 text-purple-500" />,
      audio: <Music className="w-8 h-8 text-pink-500" />,
      pdf: <FileText className="w-8 h-8 text-red-500" />,
      document: <FileText className="w-8 h-8 text-blue-500" />,
      archive: <Archive className="w-8 h-8 text-yellow-500" />,
      text: <FileText className="w-8 h-8 text-gray-500" />,
    };

    return iconMap[file.icon] || <File className="w-8 h-8 text-gray-500" />;
  };

  const handleContextMenu = (e, file) => {
    e.preventDefault();
    setSelectedFile(file);
    setContextMenu({ x: e.clientX, y: e.clientY });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
    setSelectedFile(null);
  };

  const handleDownload = async () => {
    if (selectedFile && !selectedFile.is_folder) {
      try {
        await fileService.downloadFile(selectedFile.id, selectedFile.file_name);
      } catch (error) {
        alert('Failed to download file');
      }
    }
    closeContextMenu();
  };

  const handleDelete = async () => {
    if (selectedFile && window.confirm(`Are you sure you want to delete "${selectedFile.file_name}"?`)) {
      try {
        await fileService.deleteFile(selectedFile.id);
        onRefresh();
      } catch (error) {
        alert('Failed to delete file');
      }
    }
    closeContextMenu();
  };

  const handleRename = () => {
    if (selectedFile) {
      const newName = prompt('Enter new name:', selectedFile.file_name);
      if (newName && newName !== selectedFile.file_name) {
        fileService
          .renameFile(selectedFile.id, newName)
          .then(() => {
            onRefresh();
          })
          .catch(() => {
            alert('Failed to rename file');
          });
      }
    }
    closeContextMenu();
  };

  return (
    <>
      {contextMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={closeContextMenu}
        />
      )}

      {contextMenu && (
        <div
          className="fixed z-50 bg-white rounded-lg shadow-lg border border-gray-200 py-1 min-w-[180px]"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          {!selectedFile?.is_folder && (
            <button
              onClick={handleDownload}
              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          )}

          <button
            onClick={handleRename}
            className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center space-x-2"
          >
            <Edit className="w-4 h-4" />
            <span>Rename</span>
          </button>

          <button
            onClick={handleDelete}
            className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {files.map((file) => (
          <div
            key={file.id}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer group"
            onClick={() => file.is_folder && onFileClick(file)}
            onContextMenu={(e) => handleContextMenu(e, file)}
          >
            <div className="flex items-start justify-between mb-3">
              {getFileIcon(file)}

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleContextMenu(e, file);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded transition"
              >
                <MoreVertical className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <h3 className="font-medium text-gray-900 truncate mb-1" title={file.file_name}>
              {file.file_name}
            </h3>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{file.is_folder ? 'Folder' : fileService.formatFileSize(file.file_size)}</span>
              <span>{new Date(file.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
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
