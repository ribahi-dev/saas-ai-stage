/* eslint-disable react-refresh/only-export-components */
/* eslint-disable react-hooks/set-state-in-effect */
import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import api from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'company' | 'admin';
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  loginWithGoogle: (credential: string, role?: 'student' | 'company') => Promise<void>;
  register: (userData: Record<string, unknown>) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem('access_token')));

  async function fetchUser() {
    try {
      const response = await api.get('/users/me/');
      setUser(response.data);
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      void fetchUser();
    }
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    const response = await api.post('/users/login/', {
      username,
      password,
    });
    const { access, refresh } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    await fetchUser();
  };

  const loginWithGoogle = async (
    credential: string,
    role?: 'student' | 'company',
  ) => {
    setLoading(true);
    try {
      const payload: Record<string, string> = { credential };
      if (role) payload.role = role;
      const response = await api.post('/users/google/', payload);
      const { access, refresh } = response.data as { access: string; refresh: string };
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      await fetchUser();
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: Record<string, unknown>) => {
    setLoading(true);
    try {
      const response = await api.post('/users/register/', userData);
      const { access, refresh } = response.data as { access?: string; refresh?: string };
      if (access && refresh) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        await fetchUser();
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        loginWithGoogle,
        register,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
