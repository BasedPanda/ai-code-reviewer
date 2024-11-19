// hooks/useGitHubAuth.ts

import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

interface GitHubAuthState {
  isAuthenticated: boolean;
  user: {
    login: string;
    avatarUrl: string;
    name: string;
  } | null;
  loading: boolean;
  error: Error | null;
}

const useGitHubAuth = () => {
  const [authState, setAuthState] = useState<GitHubAuthState>({
    isAuthenticated: false,
    user: null,
    loading: true,
    error: null
  });

  const checkAuthStatus = useCallback(async () => {
    try {
      const response = await api.get('/auth/status');
      setAuthState({
        isAuthenticated: response.data.isAuthenticated,
        user: response.data.user,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error : new Error('Failed to check auth status')
      }));
    }
  }, []);

  const login = useCallback(async () => {
    try {
      // Generate random state for CSRF protection
      const state = Math.random().toString(36).substring(7);
      localStorage.setItem('github_auth_state', state);

      // Get GitHub OAuth URL from backend
      const response = await api.get('/auth/github/url', {
        params: { state }
      });

      // Redirect to GitHub
      window.location.href = response.data.url;
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        error: error instanceof Error ? error : new Error('Failed to initiate login')
      }));
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        error: error instanceof Error ? error : new Error('Failed to logout')
      }));
    }
  }, []);

  const handleCallback = useCallback(async (code: string, state: string) => {
    const savedState = localStorage.getItem('github_auth_state');
    if (state !== savedState) {
      throw new Error('Invalid state parameter');
    }

    try {
      const response = await api.post('/auth/github/callback', { code });
      setAuthState({
        isAuthenticated: true,
        user: response.data.user,
        loading: false,
        error: null
      });
      localStorage.removeItem('github_auth_state');
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error : new Error('Failed to complete authentication')
      }));
    }
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  return {
    ...authState,
    login,
    logout,
    handleCallback
  };
};

export default useGitHubAuth;