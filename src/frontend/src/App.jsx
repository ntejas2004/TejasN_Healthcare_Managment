import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import PatientList from './components/PatientList';
import EncounterList from './components/EncounterList';
import Analytics from './components/Analytics';
import LoginPage from './components/LoginPage';

function AppShell() {
  const { user, loading, isAnalyst, canViewPatients } = useAuth();

  // Analyst always starts on analytics; others start on dashboard
  const defaultTab = user?.role === 'analyst' ? 'analytics' : 'dashboard';
  const [activeTab, setActiveTab] = useState(defaultTab);

  // Sync default tab when user logs in (role may change)
  useEffect(() => {
    if (user) {
      setActiveTab(user.role === 'analyst' ? 'analytics' : 'dashboard');
    }
  }, [user?.role]);

  if (loading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: '#0f172a', color: '#f1f5f9', fontSize: '1.1rem'
      }}>
        Loading…
      </div>
    );
  }

  if (!user) return <LoginPage />;

  // Guard: if analyst somehow ends up on a patient/encounter tab, redirect to analytics
  const safeTab = (!canViewPatients && (activeTab === 'patients' || activeTab === 'encounters'))
    ? 'analytics'
    : activeTab;

  const renderContent = () => {
    switch (safeTab) {
      case 'dashboard':   return <Dashboard />;
      case 'patients':    return <PatientList />;
      case 'encounters':  return <EncounterList />;
      case 'analytics':   return <Analytics />;
      default:            return isAnalyst ? <Analytics /> : <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Navbar activeTab={safeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
