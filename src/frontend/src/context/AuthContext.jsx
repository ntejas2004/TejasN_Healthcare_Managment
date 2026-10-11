// src/context/AuthContext.jsx
// Provides global auth state: user info, role, token, login/logout helpers.

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

const API = 'http://127.0.0.1:8000';

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);   // { username, role, access_token }
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage on first load
  useEffect(() => {
    const stored = localStorage.getItem('hpms_user');
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch (_) {}
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json(); // { access_token, token_type, role, username }
    const sessionUser = { username: data.username, role: data.role, access_token: data.access_token };
    localStorage.setItem('hpms_user', JSON.stringify(sessionUser));
    setUser(sessionUser);
    return sessionUser;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('hpms_user');
    setUser(null);
  }, []);

  // Helper used in api/client.js to always have the latest token
  const getToken = useCallback(() => {
    const stored = localStorage.getItem('hpms_user');
    if (!stored) return null;
    try { return JSON.parse(stored).access_token; } catch { return null; }
  }, []);

  // ── Role helpers ──────────────────────────────────────────────────────────
  const isAdministrator     = user?.role === 'administrator';
  const isClinicalOperations = user?.role === 'clinical_operations';
  const isAnalyst           = user?.role === 'analyst';

  // What each role can do:
  const canEdit           = isAdministrator || isClinicalOperations;  // create + update
  const canDelete         = isAdministrator;                          // delete only
  const canViewPatients   = isAdministrator || isClinicalOperations;  // analyst CANNOT see patient data
  const canViewAnalytics  = true;                                     // all roles can view analytics

  return (
    <AuthContext.Provider value={{
      user, loading, login, logout, getToken,
      isAdministrator, isClinicalOperations, isAnalyst,
      canEdit, canDelete, canViewPatients, canViewAnalytics,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
