import React from 'react';
import { Check } from 'lucide-react';

const FileCheckbox = ({ isSelected, visible, onToggle }) => (
  <div
    className={`transition-opacity ${visible ? 'opacity-100' : 'opacity-0'}`}
    onClick={(e) => { e.stopPropagation(); onToggle(); }}
  >
    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors cursor-pointer
      ${isSelected
        ? 'bg-blue-500 border-blue-500'
        : 'bg-white dark:bg-gray-700 border-gray-400 dark:border-gray-500 hover:border-blue-400'
      }`}
    >
      {isSelected && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
    </div>
  </div>
);

export default FileCheckbox;
