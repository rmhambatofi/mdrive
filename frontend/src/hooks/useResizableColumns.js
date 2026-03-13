import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Hook for resizable table columns.
 *
 * @param {string}   storageKey    localStorage key for persisting widths
 * @param {number[]} defaultWidths Default pixel widths for each resizable column
 * @param {number}   [minWidth=60] Minimum column width in px
 * @returns {{ widths: number[], handleMouseDown: (colIndex: number, e: MouseEvent) => void }}
 */
const useResizableColumns = (storageKey, defaultWidths, minWidth = 60) => {
  const [widths, setWidths] = useState(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length === defaultWidths.length) return parsed;
      }
    } catch {}
    return defaultWidths;
  });

  const dragRef = useRef(null);

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(widths));
  }, [widths, storageKey]);

  const handleMouseDown = useCallback((colIndex, e) => {
    e.preventDefault();
    dragRef.current = { colIndex, startX: e.clientX, startWidth: widths[colIndex] };

    const onMouseMove = (moveEvt) => {
      if (!dragRef.current) return;
      const { colIndex: ci, startX, startWidth } = dragRef.current;
      const newWidth = Math.max(minWidth, startWidth - (moveEvt.clientX - startX));
      setWidths((prev) => {
        const next = [...prev];
        next[ci] = newWidth;
        return next;
      });
    };

    const onMouseUp = () => {
      dragRef.current = null;
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [widths, minWidth]);

  return { widths, handleMouseDown };
};

export default useResizableColumns;
