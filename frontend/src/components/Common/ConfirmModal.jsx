/**
 * ConfirmModal Component
 * Generic confirmation dialog, reusable across the application.
 *
 * Props:
 *   isOpen        {boolean}   - Whether the modal is visible
 *   onClose       {function}  - Called when the user cancels or dismisses
 *   onConfirm     {function}  - Called when the user confirms
 *   title         {string}    - Modal heading
 *   message       {string}    - Body text / description
 *   confirmLabel  {string}    - Confirm button label (default: "Confirm")
 *   cancelLabel   {string}    - Cancel button label  (default: "Cancel")
 *   variant       {string}    - "danger" | "warning" | "default"  (default: "default")
 *   loading       {boolean}   - Disables buttons while an async action runs
 */
import React from 'react';
import { AlertTriangle, Trash2, Info, X } from 'lucide-react';

const VARIANT_CONFIG = {
  danger: {
    icon: Trash2,
    iconBg: 'bg-red-100 dark:bg-red-900/30',
    iconColor: 'text-red-600 dark:text-red-400',
    confirmClass: 'bg-red-600 hover:bg-red-700 text-white',
  },
  warning: {
    icon: AlertTriangle,
    iconBg: 'bg-yellow-100 dark:bg-yellow-900/30',
    iconColor: 'text-yellow-600 dark:text-yellow-400',
    confirmClass: 'bg-yellow-500 hover:bg-yellow-600 text-white',
  },
  default: {
    icon: Info,
    iconBg: 'bg-blue-100 dark:bg-blue-900/30',
    iconColor: 'text-blue-600 dark:text-blue-400',
    confirmClass: 'bg-blue-600 hover:bg-blue-700 text-white',
  },
};

const ConfirmModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = 'Are you sure?',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'default',
  loading = false,
}) => {
  if (!isOpen) return null;

  const { icon: Icon, iconBg, iconColor, confirmClass } = VARIANT_CONFIG[variant] ?? VARIANT_CONFIG.default;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full">

        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 ${iconBg} rounded-lg flex items-center justify-center`}>
              <Icon className={`w-5 h-5 ${iconColor}`} />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{title}</h2>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition disabled:opacity-50"
          >
            <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Body */}
        {message && (
          <div className="px-6 py-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end space-x-3 px-6 pb-6">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className={`px-6 py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed ${confirmClass}`}
          >
            {loading ? 'Please wait…' : confirmLabel}
          </button>
        </div>

      </div>
    </div>
  );
};

export default ConfirmModal;
