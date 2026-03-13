/**
 * File service
 * Handles file and folder operations
 */
import api from './api';

const fileService = {
  /**
   * Upload a file
   */
  uploadFile: async (file, parentFolderId = null, onProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (parentFolderId) {
      formData.append('parent_folder_id', parentFolderId);
    }

    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  },

  /**
   * Get files and folders
   */
  getFiles: async (folderId = null, page = 1, perPage = 50) => {
    const params = { page, per_page: perPage };
    if (folderId) {
      params.folder_id = folderId;
    }

    const response = await api.get('/files', { params });
    return response.data;
  },

  /**
   * Get file information
   */
  getFileInfo: async (fileId) => {
    const response = await api.get(`/files/${fileId}`);
    return response.data;
  },

  /**
   * Download a file
   */
  downloadFile: async (fileId, fileName) => {
    const response = await api.get(`/files/download/${fileId}`, {
      responseType: 'blob',
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return response.data;
  },

  /**
   * Delete a file or folder
   */
  deleteFile: async (fileId) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },

  /**
   * Create a folder
   */
  createFolder: async (folderName, parentFolderId = null) => {
    const response = await api.post('/files/folder', {
      folder_name: folderName,
      parent_folder_id: parentFolderId,
    });
    return response.data;
  },

  /**
   * Download multiple files/folders as a single ZIP archive
   * Filename format: mdrive-YYYYMMDD-HHmmss.zip
   */
  downloadZip: async (fileIds) => {
    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const zipName = `mdrive-${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}.zip`;

    const response = await api.post(
      '/files/download-zip',
      { file_ids: fileIds },
      { responseType: 'blob' }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', zipName);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // ── Recycle Bin ─────────────────────────────────────────

  getTrash: async () => {
    const response = await api.get('/files/trash');
    return response.data;
  },

  restoreFile: async (fileId) => {
    const response = await api.post(`/files/${fileId}/restore`);
    return response.data;
  },

  permanentlyDelete: async (fileId) => {
    const response = await api.delete(`/files/${fileId}/permanent`);
    return response.data;
  },

  emptyTrash: async () => {
    const response = await api.delete('/files/trash');
    return response.data;
  },

  /**
   * Rename a file or folder
   */
  renameFile: async (fileId, newName) => {
    const response = await api.put(`/files/${fileId}/rename`, {
      new_name: newName,
    });
    return response.data;
  },

  /**
   * Format file size for display
   */
  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 B';

    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let unitIndex = 0;
    let size = parseFloat(bytes);

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
  },
};

export default fileService;
