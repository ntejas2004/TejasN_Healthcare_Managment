import React from 'react';
import { Activity, Users, FileText, BarChart2, LogOut, ShieldCheck, History } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// Role display labels and badge colours
const ROLE_META = {
  administrator:       { label: 'Administrator',       color: '#0d9488' },
  clinical_operations: { label: 'Clinical Operations', color: '#6366f1' },
  analyst:             { label: 'Analyst',             color: '#f59e0b' },
};

const Navbar = ({ activeTab, setActiveTab }) => {
  const { user, logout, canViewPatients } = useAuth();
  const meta     = ROLE_META[user?.role] || { label: user?.role, color: '#94a3b8' };
  const roleColor = meta.color;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Activity size={28} color="#0d9488" />
        <span>Healthcare Patient Management</span>
      </div>

      <div className="navbar-nav">
        {/* Dashboard — visible to all roles */}
        <button
          className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <Activity size={18} /> Dashboard
        </button>

        {/* Patients — hidden from analyst */}
        {canViewPatients && (
          <button
            className={`nav-btn ${activeTab === 'patients' ? 'active' : ''}`}
            onClick={() => setActiveTab('patients')}
          >
            <Users size={18} /> Patients
          </button>
        )}

        {/* Encounters — hidden from analyst */}
        {canViewPatients && (
          <button
            className={`nav-btn ${activeTab === 'encounters' ? 'active' : ''}`}
            onClick={() => setActiveTab('encounters')}
          >
            <FileText size={18} /> Encounters
          </button>
        )}

        {/* Analytics — visible to all roles */}
        <button
          className={`nav-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart2 size={18} /> Analytics
        </button>

        {/* Audit Logs — visible to administrator & clinical operations */}
        {canViewPatients && (
          <button
            className={`nav-btn ${activeTab === 'audit-logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit-logs')}
          >
            <History size={18} /> Audit Logs
          </button>
        )}
      </div>

      {/* User info + logout */}
      <div className="navbar-user">
        <ShieldCheck size={16} color={roleColor} />
        <span className="navbar-username">{user?.username}</span>
        <span className="role-badge" style={{ background: roleColor }}>
          {meta.label}
        </span>
        <button className="btn-logout" onClick={logout} title="Sign out">
          <LogOut size={16} /> Sign out
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
