import React, { useEffect, useState } from 'react';
import { getAuditLogs } from '../api/client';
import { ShieldCheck, Search, Filter, ChevronLeft, ChevronRight, Clock, User, Tag } from 'lucide-react';

const ACTION_COLORS = {
  CREATE: '#10b981', // Emerald
  UPDATE: '#3b82f6', // Blue
  DELETE: '#ef4444', // Red
  EXPORT: '#8b5cf6', // Violet
};

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await getAuditLogs(page, limit, actionFilter, entityFilter, search);
      setLogs(data.data || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter, entityFilter, search]);

  const formatDetails = (details) => {
    if (!details) return '-';
    try {
      const parsed = JSON.parse(details);
      return Object.entries(parsed)
        .map(([k, v]) => `${k}: ${v}`)
        .join(' | ');
    } catch {
      return details;
    }
  };

  return (
    <div>
      <div className="table-header">
        <div>
          <h2>System Audit & Activity Logs</h2>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
            Comprehensive traceability of all CREATE, UPDATE, and DELETE actions ({total.toLocaleString()} total logged events)
          </span>
        </div>

        <div className="table-actions">
          {/* Search bar */}
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search by ID, User, or Details..."
              className="input-search"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              style={{ paddingLeft: '2.2rem', width: '260px' }}
            />
            <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
          </div>

          {/* Action Filter */}
          <select
            className="select-filter"
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Actions</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="DELETE">DELETE</option>
            <option value="EXPORT">EXPORT</option>
          </select>

          {/* Entity Filter */}
          <select
            className="select-filter"
            value={entityFilter}
            onChange={(e) => { setEntityFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Entities</option>
            <option value="Patient">Patient</option>
            <option value="Encounter">Encounter</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Audit Trail...</div>
      ) : logs.length === 0 ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
          No audit logs recorded yet for this criteria. Perform a patient or encounter creation, edit, or delete to see live activity.
        </div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Target ID</th>
                <th>Performed By</th>
                <th>Role</th>
                <th>Change Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => {
                const actionColor = ACTION_COLORS[log.action] || '#94a3b8';
                return (
                  <tr key={log.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '0.85rem', color: '#94a3b8' }}>
                      <Clock size={13} style={{ display: 'inline', marginRight: '4px', verticalAlign: '-1px' }} />
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : '-'}
                    </td>
                    <td>
                      <span
                        style={{
                          background: `${actionColor}20`,
                          color: actionColor,
                          border: `1px solid ${actionColor}40`,
                          padding: '0.2rem 0.55rem',
                          borderRadius: '9999px',
                          fontWeight: '700',
                          fontSize: '0.75rem',
                          letterSpacing: '0.04em'
                        }}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td>
                      <strong>{log.entity_type}</strong>
                    </td>
                    <td>
                      <code>{log.entity_id}</code>
                    </td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', color: '#e2e8f0', fontWeight: '500' }}>
                        <User size={14} color="#0d9488" /> {log.performed_by}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'capitalize' }}>
                        {log.user_role?.replace('_', ' ') || 'User'}
                      </span>
                    </td>
                    <td style={{ maxWidth: '340px', fontSize: '0.82rem', color: '#cbd5e1', wordBreak: 'break-word' }}>
                      {formatDetails(log.details)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="pagination-container">
        <div>
          Showing page {page} of {Math.max(1, Math.ceil(total / limit))} ({total.toLocaleString()} total logged events)
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="btn-secondary"
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <button
            className="btn-secondary"
            disabled={page >= Math.ceil(total / limit)}
            onClick={() => setPage((p) => p + 1)}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
