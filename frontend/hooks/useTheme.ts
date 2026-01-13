import { useThemeStore } from "@/store/theme-store";
import { useEffect } from "react";

type Theme = "light" | "dark" | "system";

/**
 * Custom hook for theme management
 * Provides theme state and actions with automatic DOM updates
 */
export function useTheme() {
  const { theme, setTheme, resolvedTheme } = useThemeStore();

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    
    if (resolvedTheme === "dark") {
      root.classList.add("dark");
      root.classList.remove("light");
    } else {
      root.classList.add("light");
      root.classList.remove("dark");
    }
  }, [resolvedTheme]);

  // Listen for system theme changes
  useEffect(() => {
    if (theme !== "system") return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      const root = document.documentElement;
      if (e.matches) {
        root.classList.add("dark");
        root.classList.remove("light");
      } else {
        root.classList.add("light");
        root.classList.remove("dark");
      }
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme]);

  return {
    // State
    theme,
    resolvedTheme,
    isDark: resolvedTheme === "dark",
    isLight: resolvedTheme === "light",
    isSystem: theme === "system",
    
    // Actions
    setTheme,
    setLight: () => setTheme("light"),
    setDark: () => setTheme("dark"),
    setSystem: () => setTheme("system"),
    toggle: () => setTheme(resolvedTheme === "dark" ? "light" : "dark"),
  };
}


