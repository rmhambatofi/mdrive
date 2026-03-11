/**
 * ThemeContext
 * Manages light / dark / system theme preference.
 * Persists to localStorage and applies the `dark` class to <html>.
 */
import { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext(null);

const applyTheme = (theme) => {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else if (theme === 'light') {
    root.classList.remove('dark');
  } else {
    // system
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.classList.toggle('dark', prefersDark);
  }
};

export const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(() => {
    const saved = localStorage.getItem('theme') || 'system';
    // Apply synchronously before first render to avoid flash
    applyTheme(saved);
    return saved;
  });

  const setTheme = (newTheme) => {
    // Apply to DOM immediately, before React re-renders
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    setThemeState(newTheme);
  };

  // Re-apply when OS preference changes and theme is 'system'
  useEffect(() => {
    if (theme !== 'system') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e) => document.documentElement.classList.toggle('dark', e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within a ThemeProvider');
  return context;
};

export default ThemeContext;
