/**
 * SortSelector Component
 * Dropdown to choose sort field and direction, matching OneDrive style.
 */
import React, { useState, useRef, useEffect } from 'react';
import { ArrowUpDown, Check, ChevronDown } from 'lucide-react';

const SORT_FIELDS = [
  { key: 'type', label: 'Type' },
  { key: 'name', label: 'Name' },
  { key: 'modified', label: 'Modified' },
  { key: 'size', label: 'File size' },
];

const SORT_DIRECTIONS = [
  { key: 'asc', label: 'Ascending' },
  { key: 'desc', label: 'Descending' },
];

const SortSelector = ({ sortField, sortDirection, onChange }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleFieldClick = (key) => {
    onChange({ field: key, direction: sortDirection });
  };

  const handleDirectionClick = (key) => {
    onChange({ field: sortField, direction: key });
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
      >
        <ArrowUpDown className="w-4 h-4" />
        <span>Sort</span>
        <ChevronDown className="w-3.5 h-3.5" />
      </button>

      {open && (
        <div className="absolute right-0 mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-30 py-1">
          {SORT_FIELDS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleFieldClick(key)}
              className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <span className="flex-1 text-left">{label}</span>
              {sortField === key && <Check className="w-4 h-4 text-blue-500" />}
            </button>
          ))}

          <div className="border-t border-gray-200 dark:border-gray-700 my-1" />

          {SORT_DIRECTIONS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleDirectionClick(key)}
              className="w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <span className="flex-1 text-left">{label}</span>
              {sortDirection === key && <Check className="w-4 h-4 text-blue-500" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * Sort an array of files client-side.
 * Folders always come first, then sorted by the chosen field.
 */
export const sortFiles = (files, field, direction) => {
  const dir = direction === 'desc' ? -1 : 1;

  return [...files].sort((a, b) => {
    // Folders always first
    if (a.is_folder && !b.is_folder) return -1;
    if (!a.is_folder && b.is_folder) return 1;

    let cmp = 0;
    switch (field) {
      case 'name':
        cmp = (a.file_name || '').localeCompare(b.file_name || '', undefined, { sensitivity: 'base' });
        break;
      case 'modified':
        cmp = new Date(a.updated_at || 0) - new Date(b.updated_at || 0);
        break;
      case 'size':
        cmp = (a.file_size || 0) - (b.file_size || 0);
        break;
      case 'type': {
        const extA = (a.file_name || '').split('.').pop().toLowerCase();
        const extB = (b.file_name || '').split('.').pop().toLowerCase();
        cmp = extA.localeCompare(extB, undefined, { sensitivity: 'base' });
        break;
      }
      default:
        cmp = (a.file_name || '').localeCompare(b.file_name || '', undefined, { sensitivity: 'base' });
    }

    return cmp * dir;
  });
};

export default SortSelector;
