import { useAuthStore } from "@/store/auth-store";

/**
 * Custom hook for authentication state and actions
 * Provides convenient access to auth store with common auth operations
 */
export function useAuth() {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    setUser,
    setToken,
    clearAuth,
    refreshUser,
  } = useAuthStore();

  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading,
    
    // Actions
    login,
    register,
    logout,
    setUser,
    setToken,
    clearAuth,
    refreshUser,
    
    // Helpers
    isAdmin: user?.role === "admin",
    isUser: user?.role === "user",
    userId: user?.id,
    username: user?.username,
    email: user?.email,
    fullName: user?.full_name,
  };
}

