/**
 * ViewModeSelector Component
 * Dropdown to switch between Tiles, List, and Compact List views.
 */
import React, { useState, useRef, useEffect } from 'react';
import { LayoutGrid, List, AlignJustify, Check, ChevronDown } from 'lucide-react';

const VIEW_MODES = [
  { key: 'list', label: 'List', icon: List },
  { key: 'compact', label: 'Compact List', icon: AlignJustify },
  { key: 'tiles', label: 'Tiles', icon: LayoutGrid },
];

const ViewModeSelector = ({ value, onChange }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const current = VIEW_MODES.find((m) => m.key === value) || VIEW_MODES[2];
  const CurrentIcon = current.icon;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
      >
        <CurrentIcon className="w-4 h-4" />
        <ChevronDown className="w-3.5 h-3.5" />
      </button>

      {open && (
        <div className="absolute right-0 mt-1 w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-30 py-1">
          {VIEW_MODES.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => { onChange(key); setOpen(false); }}
              className="w-full flex items-center space-x-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <Icon className="w-4 h-4" />
              <span className="flex-1 text-left">{label}</span>
              {value === key && <Check className="w-4 h-4 text-blue-500" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ViewModeSelector;
