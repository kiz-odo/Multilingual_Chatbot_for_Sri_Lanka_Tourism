import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User } from "@/types";
import apiClient from "@/lib/api-client";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  clearAuth: () => void;
  refreshUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.auth.login(username, password);
          const { access_token, user } = response.data;
          
          apiClient.setToken(access_token);
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({ isLoading: false });
          // Preserve the original error for proper handling in the UI
          // Network errors will be caught and handled in the login page
          throw error;
        }
      },

      register: async (data) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.auth.register(data);
          const { access_token, user } = response.data;
          
          apiClient.setToken(access_token);
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          await apiClient.auth.logout();
        } catch (error) {
          console.error("Logout error:", error);
        } finally {
          apiClient.clearAuth();
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      },

      setUser: (user: User) => {
        set({ user, isAuthenticated: true });
      },

      setToken: (token: string) => {
        apiClient.setToken(token);
        set({ token, isAuthenticated: true });
      },

      clearAuth: () => {
        apiClient.clearAuth();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      refreshUser: async () => {
        try {
          const response = await apiClient.users.getMe();
          set({ user: response.data });
        } catch (error) {
          console.error("Failed to refresh user:", error);
        }
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

