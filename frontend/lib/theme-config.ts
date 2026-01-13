/**
 * Unified Theme Configuration for Sri Lanka Tourism App
 * This ensures consistent design across all pages
 */

export const themeConfig = {
  colors: {
    primary: {
      50: "#f0fdfa",
      100: "#ccfbf1",
      200: "#99f6e4",
      300: "#5eead4",
      400: "#2dd4bf",
      500: "#14b8a6",
      600: "#0d9488",
      700: "#0f766e",
      800: "#115e59",
      900: "#134e4a",
    },
    ocean: {
      50: "#eff6ff",
      100: "#dbeafe",
      200: "#bfdbfe",
      300: "#93c5fd",
      400: "#60a5fa",
      500: "#3b82f6",
      600: "#2563eb",
      700: "#1d4ed8",
      800: "#1e40af",
      900: "#1e3a8a",
    },
    green: {
      50: "#f0fdf4",
      100: "#dcfce7",
      200: "#bbf7d0",
      300: "#86efac",
      400: "#4ade80",
      500: "#22c55e",
      600: "#16a34a",
      700: "#15803d",
      800: "#166534",
      900: "#14532d",
    },
    accent: {
      red: "#ef4444",
      orange: "#f97316",
      yellow: "#eab308",
      purple: "#a855f7",
    },
  },
  spacing: {
    container: {
      mobile: "1rem",
      tablet: "2rem",
      desktop: "3rem",
    },
    section: {
      mobile: "2rem",
      tablet: "3rem",
      desktop: "4rem",
    },
  },
  borderRadius: {
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    xl: "1.5rem",
    full: "9999px",
  },
  shadows: {
    sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    md: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
    lg: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
    xl: "0 20px 25px -5px rgb(0 0 0 / 0.1)",
  },
  breakpoints: {
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },
  typography: {
    fontFamily: {
      sans: "var(--font-geist-sans), system-ui, -apple-system, sans-serif",
      mono: "var(--font-geist-mono), monospace",
    },
    sizes: {
      xs: "0.75rem",
      sm: "0.875rem",
      base: "1rem",
      lg: "1.125rem",
      xl: "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem",
      "4xl": "2.25rem",
      "5xl": "3rem",
      "6xl": "3.75rem",
      "7xl": "4.5rem",
    },
  },
  components: {
    button: {
      primary: "bg-teal-600 hover:bg-teal-700 text-white",
      secondary: "bg-ocean-blue-600 hover:bg-ocean-blue-700 text-white",
      success: "bg-green-600 hover:bg-green-700 text-white",
      danger: "bg-red-600 hover:bg-red-700 text-white",
      outline: "border-2 border-gray-300 hover:border-teal-600 text-gray-700 hover:text-teal-600",
    },
    card: {
      base: "bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow",
      elevated: "bg-white rounded-xl shadow-lg",
    },
    badge: {
      primary: "bg-teal-100 text-teal-800",
      secondary: "bg-ocean-blue-100 text-ocean-blue-800",
      success: "bg-green-100 text-green-800",
      warning: "bg-yellow-100 text-yellow-800",
      danger: "bg-red-100 text-red-800",
    },
  },
};

export default themeConfig;



