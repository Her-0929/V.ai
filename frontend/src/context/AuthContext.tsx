'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api } from '../lib/api';
import { UserResponse } from '../types/api';

interface AuthContextType {
  user: UserResponse | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (usernameOrEmail: string, password?: string) => Promise<boolean>;
  register: (username: string, email: string, password?: string) => Promise<boolean>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const initAuth = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const storedToken = localStorage.getItem('her_ai_token');
      if (storedToken) {
        setToken(storedToken);
        const me = await api.getMe();
        setUser(me);
      } else {
        // Auto-login with default companion user 'vivek' for seamless out-of-the-box experience
        try {
          const authRes = await api.login('vivek', 'HerAiVivekSecure2026!');
          setToken(authRes.access_token);
          setUser(authRes.user);
        } catch {
          // If user doesn't exist yet in the database, automatically register them!
          try {
            const regRes = await api.register('vivek', 'vivek@her-ai.internal', 'HerAiVivekSecure2026!');
            setToken(regRes.access_token);
            setUser(regRes.user);
            console.info('Created and authenticated default companion user.');
          } catch (regErr) {
            console.warn('Auto-register failed:', regErr);
          }
        }
      }
    } catch (err: unknown) {
      console.warn('Session verification error:', err);
      api.logout();
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  const login = async (usernameOrEmail: string, password?: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.login(usernameOrEmail, password);
      setToken(res.access_token);
      setUser(res.user);
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed.';
      setError(msg);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password?: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.register(username, email, password);
      setToken(res.access_token);
      setUser(res.user);
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed.';
      setError(msg);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const me = await api.getMe();
      setUser(me);
    } catch (err) {
      console.warn('Failed to refresh user profile:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        error,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
