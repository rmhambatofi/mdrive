import React from 'react';

const FileRenameInput = ({ value, onChange, onConfirm, onCancel, centered = false }) => (
  <input
    autoFocus
    value={value}
    onChange={(e) => onChange(e.target.value)}
    onBlur={onConfirm}
    onKeyDown={(e) => {
      if (e.key === 'Enter') onConfirm();
      if (e.key === 'Escape') onCancel();
    }}
    onClick={(e) => e.stopPropagation()}
    className={`w-full text-xs border border-blue-400 dark:border-blue-500 rounded px-1 py-0.5 outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 ${centered ? 'text-center' : ''}`}
  />
);

export default FileRenameInput;
