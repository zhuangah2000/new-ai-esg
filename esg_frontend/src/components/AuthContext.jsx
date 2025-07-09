import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sessionReady, setSessionReady] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  // Check authentication status
  const checkAuth = async () => {
    try {
      console.log('🔍 Checking authentication status...');
      const response = await fetch(`${API_BASE_URL}/auth/current-user`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('📡 Auth check response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Auth check response:', data);
        
        if (data.success && data.data) {
          console.log('🎉 User is authenticated:', data.data.username);
          setUser(data.data);
          setIsAuthenticated(true);
          setSessionReady(true);
        } else {
          console.log('❌ User not authenticated - clearing state');
          setUser(null);
          setIsAuthenticated(false);
          setSessionReady(false);
        }
      } else {
        console.log('❌ Auth check failed with status:', response.status);
        setUser(null);
        setIsAuthenticated(false);
        setSessionReady(false);
      }
    } catch (error) {
      console.error('❌ Auth check error:', error);
      setUser(null);
      setIsAuthenticated(false);
      setSessionReady(false);
    } finally {
      setLoading(false);
      console.log('✅ Auth check completed');
    }
  };

  // Login function - CORRECT FIX for nested response structure
  const login = async (username, password) => {
    try {
      console.log('🔐 Attempting login for:', username);
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      console.log('📡 Login response:', data);

      // CORRECT FIX: Handle the actual nested structure
      // Response: { success: true, data: { message: "Login successful", user: {...} } }
      if (response.ok && data.success && data.data && data.data.message === 'Login successful' && data.data.user) {
        console.log('✅ Login successful for:', data.data.user.username);
        
        // Use the nested user data: data.data.user
        setUser(data.data.user);
        setIsAuthenticated(true);
        
        // Small delay to ensure session is established
        setTimeout(() => {
          setSessionReady(true);
          console.log('✅ Session established after login');
        }, 300);
        
        return { success: true, data: data.data.user };
      } else {
        console.log('❌ Login failed:', data.error || data.data?.error || 'Invalid credentials');
        setUser(null);
        setIsAuthenticated(false);
        setSessionReady(false);
        return { success: false, error: data.error || data.data?.error || 'Login failed' };
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      setUser(null);
      setIsAuthenticated(false);
      setSessionReady(false);
      return { success: false, error: 'Network error occurred' };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      console.log('🚪 Logging out...');
      setSessionReady(false);
      
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        console.log('✅ Logout successful');
      } else {
        console.log('⚠️ Logout response not OK, but proceeding with local logout');
      }
    } catch (error) {
      console.error('❌ Logout error:', error);
    } finally {
      // Always clear local state regardless of server response
      setUser(null);
      setIsAuthenticated(false);
      setSessionReady(false);
      console.log('🧹 Local auth state cleared');
    }
  };

  // Refresh authentication
  const refreshAuth = async () => {
    setLoading(true);
    setSessionReady(false);
    await checkAuth();
  };

  // Check authentication on mount
  useEffect(() => {
    console.log('🚀 AuthProvider mounted, checking authentication...');
    checkAuth();
  }, []);

  // Debug logging for state changes
  useEffect(() => {
    console.log('🔄 Auth state changed:', {
      isAuthenticated,
      sessionReady,
      user: user?.username || null,
      loading,
      userObject: user
    });
  }, [isAuthenticated, sessionReady, user, loading]);

  const value = {
    user,
    isAuthenticated,
    sessionReady,
    loading,
    login,
    logout,
    refreshAuth,
    checkAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

