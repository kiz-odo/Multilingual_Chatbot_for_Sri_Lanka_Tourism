import { create } from "zustand";

type Theme = "light" | "dark" | "system";

interface ThemeStore {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: "light" | "dark";
}

export const useThemeStore = create<ThemeStore>((set) => {
  // Initialize theme from localStorage if available
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("theme-storage");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        const theme = parsed.state?.theme || "system";
        const resolvedTheme = theme === "system" 
          ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
          : theme;
        return {
          theme,
          resolvedTheme,
          setTheme: (newTheme: Theme) => {
            const resolved = newTheme === "system"
              ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
              : newTheme;
            set({ theme: newTheme, resolvedTheme: resolved });
            localStorage.setItem("theme-storage", JSON.stringify({ state: { theme: newTheme, resolvedTheme: resolved } }));
          },
        };
      } catch {
        // Fall through to default
      }
    }
  }

  return {
    theme: "system",
    resolvedTheme: typeof window !== "undefined" 
      ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
      : "light",
    setTheme: (theme: Theme) => {
      const resolved = theme === "system"
        ? (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
        : theme;
      set({ theme, resolvedTheme: resolved });
      if (typeof window !== "undefined") {
        localStorage.setItem("theme-storage", JSON.stringify({ state: { theme, resolvedTheme: resolved } }));
      }
    },
  };
});

