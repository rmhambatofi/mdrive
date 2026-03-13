import React from 'react';
import { File, FileText, Image, Music, Video, Archive } from 'lucide-react';
import FolderIcon from '../Common/FolderIcon';

/**
 * Return the appropriate icon element for a file.
 * @param {object} file    - File object with is_folder, icon, item_count, file_name
 * @param {'lg'|'sm'} size - Icon size variant
 */
export const getFileIcon = (file, size = 'lg') => {
  if (size === 'lg') {
    if (file.is_folder) return <FolderIcon className="w-20 h-20" itemCount={file.item_count} />;
    const map = {
      image: <Image className="w-10 h-10 text-green-500" />,
      video: <Video className="w-10 h-10 text-purple-500" />,
      audio: <Music className="w-10 h-10 text-pink-500" />,
      pdf: <FileText className="w-10 h-10 text-red-500" />,
      document: <FileText className="w-10 h-10 text-blue-500" />,
      archive: <Archive className="w-10 h-10 text-yellow-600" />,
      text: <FileText className="w-10 h-10 text-gray-500" />,
    };
    return map[file.icon] || <File className="w-10 h-10 text-gray-500" />;
  }

  if (file.is_folder) return <FolderIcon className="w-5 h-5" />;
  const map = {
    image: <Image className="w-5 h-5 text-green-500" />,
    video: <Video className="w-5 h-5 text-purple-500" />,
    audio: <Music className="w-5 h-5 text-pink-500" />,
    pdf: <FileText className="w-5 h-5 text-red-500" />,
    document: <FileText className="w-5 h-5 text-blue-500" />,
    archive: <Archive className="w-5 h-5 text-yellow-600" />,
    text: <FileText className="w-5 h-5 text-gray-500" />,
  };
  return map[file.icon] || <File className="w-5 h-5 text-gray-500" />;
};

/**
 * Format an ISO date string for display.
 */
export const formatDate = (isoString) => {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
};
