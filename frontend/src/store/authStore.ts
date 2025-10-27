import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, LoginCredentials, RegisterData } from '@/types';
import { authAPI } from '@/services/api';
import toast from 'react-hot-toast';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true });
        try {
          const response = await authAPI.login(credentials);
          
          // Store tokens
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });
          
          toast.success('Welcome back!');
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Login failed';
          toast.error(message);
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          console.log('Registering user:', { username: data.username, email: data.email });
          const response = await authAPI.register(data);
          console.log('Registration response:', response);
          
          // Store tokens
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });
          
          toast.success('Account created successfully!');
        } catch (error: any) {
          set({ isLoading: false });
          console.error('Registration error:', error);
          console.error('Error response:', error.response?.data);
          const message = error.response?.data?.detail || error.message || 'Registration failed';
          toast.error(message);
          throw error;
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear tokens from localStorage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          
          set({
            user: null,
            isAuthenticated: false,
          });
          toast.success('Logged out successfully');
        }
      },

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ user: null, isAuthenticated: false, isLoading: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authAPI.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          console.error('Auth check failed:', error);
          set({ user: null, isAuthenticated: false, isLoading: false });
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          // Don't show error toast on auth check failure (silent fail)
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
