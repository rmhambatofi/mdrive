/**
 * Breadcrumb Component
 * Shows navigation path through folders
 */
import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

const Breadcrumb = ({ items, onNavigate }) => {
  return (
    <nav className="flex items-center space-x-2 text-sm mb-6">
      <button
        onClick={() => onNavigate(null)}
        className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 transition"
      >
        <Home className="w-4 h-4" />
        <span>My Files</span>
      </button>

      {items.map((item, index) => (
        <React.Fragment key={item.id}>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <button
            onClick={() => onNavigate(item.id)}
            className={`hover:text-gray-900 transition ${
              index === items.length - 1
                ? 'text-gray-900 font-medium'
                : 'text-gray-600'
            }`}
          >
            {item.name}
          </button>
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumb;
