import React, { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import type { User, LoginRequest, RegisterRequest, AuthContext } from './types';
import { api } from './api';

// Create Auth Context
const AuthContextInstance = createContext<AuthContext | undefined>(undefined);

// Auth Provider Component
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const savedToken = localStorage.getItem('authToken');
        const savedUser = localStorage.getItem('user');

        if (savedToken && savedUser) {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
          
          // Verify token is still valid
          try {
            const currentUser = await api.getCurrentUser();
            setUser(currentUser);
            localStorage.setItem('user', JSON.stringify(currentUser));
          } catch (error) {
            // Token is invalid, clear auth
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            setToken(null);
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      setIsLoading(true);
      const authResponse = await api.login(credentials);
      const token = authResponse.access_token;
      
      // Store token
      localStorage.setItem('authToken', token);
      setToken(token);
      
      // Get user information
      const user = await api.getCurrentUser();
      localStorage.setItem('user', JSON.stringify(user));
      setUser(user);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    try {
      setIsLoading(true);
      const user = await api.register(data);
      
      // Auto-login after registration
      await login({
        username: data.username,
        password: data.password
      });
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const refreshToken = async () => {
    try {
      const authResponse = await api.refreshToken();
      const newToken = authResponse.access_token;
      
      localStorage.setItem('authToken', newToken);
      setToken(newToken);
      
      // Update user information
      const user = await api.getCurrentUser();
      localStorage.setItem('user', JSON.stringify(user));
      setUser(user);
    } catch (error) {
      // If refresh fails, logout user
      logout();
      throw error;
    }
  };

  const value: AuthContext = {
    user,
    token,
    login,
    register,
    logout,
    refreshToken,
    isLoading,
    isAuthenticated: !!token && !!user,
  };

  return (
    <AuthContextInstance.Provider value={value}>
      {children}
    </AuthContextInstance.Provider>
  );
}

// Hook to use auth context
export function useAuth(): AuthContext {
  const context = useContext(AuthContextInstance);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Helper functions for role-based access
export function hasRole(user: User | null, roles: string[]): boolean {
  if (!user) return false;
  return roles.includes(user.role);
}

export function canAccessDepartment(user: User | null, department: string): boolean {
  if (!user) return false;
  if (user.role === 'admin') return true;
  return user.department === department;
}

export function canManagePatients(user: User | null): boolean {
  if (!user) return false;
  return ['doctor', 'admin'].includes(user.role);
}

export function canViewSensitiveDocuments(user: User | null): boolean {
  if (!user) return false;
  return ['doctor', 'admin'].includes(user.role);
}

export function canCreateDocuments(user: User | null): boolean {
  if (!user) return false;
  return ['doctor', 'nurse', 'admin'].includes(user.role);
}

export function getUserDisplayName(user: User | null): string {
  if (!user) return 'Unknown User';
  
  const roleMap = {
    doctor: 'Dr.',
    nurse: 'Nurse',
    admin: 'Admin'
  };
  
  const prefix = roleMap[user.role] || '';
  return prefix ? `${prefix} ${user.username}` : user.username;
}

export function getRoleDisplayName(role: string): string {
  const roleMap = {
    doctor: 'Doctor',
    nurse: 'Nurse',
    admin: 'Administrator'
  };
  
  return roleMap[role as keyof typeof roleMap] || role;
}

export function getDepartmentDisplayName(department: string): string {
  const departmentMap = {
    cardiology: 'Cardiology',
    neurology: 'Neurology',
    pediatrics: 'Pediatrics',
    oncology: 'Oncology',
    emergency: 'Emergency Medicine',
    endocrinology: 'Endocrinology',
    general: 'General Medicine'
  };
  
  return departmentMap[department as keyof typeof departmentMap] || department;
}

// Token expiration checker
export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
}

// Auto token refresh setup
export function setupTokenRefresh() {
  const token = localStorage.getItem('authToken');
  if (!token) return;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expirationTime = payload.exp * 1000;
    const currentTime = Date.now();
    const timeUntilExpiration = expirationTime - currentTime;
    
    // Refresh token 5 minutes before expiration
    const refreshTime = Math.max(timeUntilExpiration - 5 * 60 * 1000, 0);
    
    if (refreshTime > 0) {
      setTimeout(() => {
        api.refreshToken().catch(() => {
          // If refresh fails, logout user
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
        });
      }, refreshTime);
    }
  } catch (error) {
    console.error('Error setting up token refresh:', error);
  }
}