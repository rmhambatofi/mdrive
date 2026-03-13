import React, { useId } from 'react';

/**
 * FolderIcon — Fluent-style folder icon with optional item count badge.
 *
 * @param {string}  [className='w-10 h-10']  Tailwind size classes
 * @param {number}  [itemCount]              Number shown in the bottom-left corner
 */
const FolderIcon = ({ className = 'w-10 h-10', itemCount }) => {
  // Unique gradient ID so multiple icons on the same page don't clash
  const uid = useId();
  const gradientId = `folder-front-${uid}`;

  return (
    <div className={`relative inline-flex ${className}`}>
      <svg
        className="w-full h-full"
        viewBox="0 0 112 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id={gradientId} x1="56" y1="16" x2="56" y2="80" gradientUnits="userSpaceOnUse">
            <stop stopColor="#FFD75E" />
            <stop offset="1" stopColor="#F2A600" />
          </linearGradient>
        </defs>

        {/* Back panel with tab */}
        <path
          d="M52 8L46.7333 2.73333C44.9829 0.983035 42.6088 0 40.1333 0H5.33333C2.38781 0 0 2.38781 0 5.33333V74.6667C0 77.6122 2.38781 80 5.33333 80H106.667C109.612 80 112 77.6122 112 74.6667V13.3333C112 10.3878 109.612 8 106.667 8H52Z"
          fill="#F5B800"
        />

        {/* Front panel */}
        <path
          d="M52 8L46.7333 13.2667C44.9829 15.017 42.6088 16.0002 40.1333 16H0V74.6667C0 77.6122 2.38781 80 5.33333 80C5.33333 80 103.721 80 106.667 80C109.612 80 112 77.6122 112 74.6667V13.3333C112 10.3878 109.612 8 106.667 8H52Z"
          fill={`url(#${gradientId})`}
        />

        {/* Bottom edge shadow */}
        <path
          d="M5.25024 79.992C6.50024 79.992 106.75 79.992 106.75 79.992C108 79.99 109.5 79.49 110.47 78.392L110.1 78.57C109 78.992 108.5 78.99 108.055 78.992L4.14931 78.992C3.50024 78.99 3.00024 78.99 2.00036 78.572L1.53027 78.39C2.50024 79.49 4.00024 79.992 5.25024 79.992Z"
          fill="#B64D07"
        />

        {/* Tab highlight */}
        <path
          d="M47.596 14.404L54 8H52L46.7333 13.2667C44.9829 15.017 42.6088 16.0002 40.1333 16H0V17.3333H40.524C43.1765 17.3335 45.7205 16.2797 47.596 14.404Z"
          fill="#FFFFFF"
          opacity="0.4"
        />
      </svg>

      {/* Item count badge */}
      {itemCount != null && (
        <span
          className="absolute bottom-[18%] left-[10%] text-[0.75em] font-semibold leading-none select-none"
          style={{ color: '#8F3900' }}
        >
          {itemCount}
        </span>
      )}
    </div>
  );
};

export default FolderIcon;
