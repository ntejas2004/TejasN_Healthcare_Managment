import React, { useEffect, useState } from 'react';
import { getEncounters, createEncounter, updateEncounter, deleteEncounter, downloadExport } from '../api/client';
import { Plus, Search, Trash2, Edit, ChevronLeft, ChevronRight, X, Filter, Download, FileSpreadsheet } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const EncounterList = () => {
  const { canEdit, canDelete } = useAuth();
  const [encounters, setEncounters] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [readmittedFilter, setReadmittedFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingEncounter, setEditingEncounter] = useState(null);
  const [formData, setFormData] = useState({
    encounter_id: 0,
    patient_nbr: '',
    time_in_hospital: 3,
    num_lab_procedures: 40,
    num_procedures: 1,
    num_medications: 12,
    medical_specialty: 'InternalMedicine',
    readmitted: 'NO'
  });

  const fetchEncounters = async () => {
    setLoading(true);
    try {
      const data = await getEncounters(page, 15, search, readmittedFilter);
      setEncounters(data.data);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch encounters:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEncounters();
  }, [page, search, readmittedFilter]);

  const handleOpenCreate = () => {
    setEditingEncounter(null);
    setFormData({
      encounter_id: Math.floor(100000 + Math.random() * 900000),
      patient_nbr: '8222157',
      time_in_hospital: 3,
      num_lab_procedures: 40,
      num_procedures: 1,
      num_medications: 12,
      medical_specialty: 'InternalMedicine',
      readmitted: 'NO'
    });
    setShowModal(true);
  };

  const handleOpenEdit = (enc) => {
    setEditingEncounter(enc);
    setFormData({
      encounter_id: enc.encounter_id,
      patient_nbr: enc.patient_nbr,
      time_in_hospital: enc.time_in_hospital || 1,
      num_lab_procedures: enc.num_lab_procedures || 0,
      num_procedures: enc.num_procedures || 0,
      num_medications: enc.num_medications || 0,
      medical_specialty: enc.medical_specialty || 'General',
      readmitted: enc.readmitted || 'NO'
    });
    setShowModal(true);
  };

  const handleDelete = async (encounterId) => {
    if (window.confirm(`Delete encounter record #${encounterId}?`)) {
      try {
        await deleteEncounter(encounterId);
        fetchEncounters();
      } catch (err) {
        alert('Error deleting encounter');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingEncounter) {
        await updateEncounter(editingEncounter.encounter_id, {
          time_in_hospital: parseInt(formData.time_in_hospital),
          num_lab_procedures: parseInt(formData.num_lab_procedures),
          num_procedures: parseInt(formData.num_procedures),
          num_medications: parseInt(formData.num_medications),
          medical_specialty: formData.medical_specialty,
          readmitted: formData.readmitted
        });
      } else {
        await createEncounter({
          ...formData,
          encounter_id: parseInt(formData.encounter_id),
          time_in_hospital: parseInt(formData.time_in_hospital),
          num_lab_procedures: parseInt(formData.num_lab_procedures),
          num_procedures: parseInt(formData.num_procedures),
          num_medications: parseInt(formData.num_medications)
        });
      }
      setShowModal(false);
      fetchEncounters();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error saving encounter');
    }
  };

  const renderBadge = (status) => {
    if (status === '<30') return <span className="badge badge-danger">Readmitted &lt;30d</span>;
    if (status === '>30') return <span className="badge badge-warning">Readmitted &gt;30d</span>;
    return <span className="badge badge-success">No Readmit</span>;
  };

  return (
    <div className="table-card">
      <div className="table-header">
        <div>
          <h2 className="table-title">Hospital Encounter Management</h2>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
            Showing {encounters.length} of {total.toLocaleString()} encounter records
          </span>
        </div>

        <div className="table-actions">
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search by Patient, Specialty..."
              className="input-search"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              style={{ paddingLeft: '2.2rem', width: '220px' }}
            />
            <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
          </div>

          <select
            className="select-filter"
            value={readmittedFilter}
            onChange={(e) => { setReadmittedFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Readmission Statuses</option>
            <option value="<30">Readmitted &lt;30 Days</option>
            <option value=">30">Readmitted &gt;30 Days</option>
            <option value="NO">No Readmission</option>
          </select>

          <button
            className="btn-secondary"
            onClick={() => downloadExport('/export/encounters/csv', 'encounters_export.csv')}
            title="Export Encounter data to CSV"
          >
            <Download size={15} /> Export CSV
          </button>

          <button
            className="btn-secondary"
            onClick={() => downloadExport('/export/encounters/excel', 'encounters_export.xlsx')}
            title="Export Encounter data to Excel"
          >
            <FileSpreadsheet size={15} /> Export Excel
          </button>

          {canEdit && (
            <button className="btn-primary" onClick={handleOpenCreate}>
              <Plus size={16} /> New Encounter
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Encounters...</div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Encounter ID</th>
                <th>Patient ID</th>
                <th>Specialty</th>
                <th>Stay (Days)</th>
                <th>Labs</th>
                <th>Meds</th>
                <th>Readmitted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {encounters.map((enc) => (
                <tr key={enc.encounter_id}>
                  <td><strong>#{enc.encounter_id}</strong></td>
                  <td>{enc.patient_nbr}</td>
                  <td>{enc.medical_specialty || 'General'}</td>
                  <td>{enc.time_in_hospital} days</td>
                  <td>{enc.num_lab_procedures}</td>
                  <td>{enc.num_medications}</td>
                  <td>{renderBadge(enc.readmitted)}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {canEdit && (
                        <button className="btn-secondary" onClick={() => handleOpenEdit(enc)}>
                          <Edit size={14} /> Edit
                        </button>
                      )}
                      {canDelete && (
                        <button className="btn-danger" onClick={() => handleDelete(enc.encounter_id)}>
                          <Trash2 size={14} /> Delete
                        </button>
                      )}
                      {!canEdit && !canDelete && (
                        <span style={{ color: '#64748b', fontSize: '0.8rem' }}>View only</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="pagination-container">
        <div>Page {page} of {Math.ceil(total / 15)}</div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="btn-secondary"
            disabled={page === 1}
            onClick={() => setPage(p => Math.max(p - 1, 1))}
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <button
            className="btn-secondary"
            disabled={page * 15 >= total}
            onClick={() => setPage(p => p + 1)}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Modal Form */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingEncounter ? 'Edit Encounter' : 'Record New Hospital Encounter'}</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Encounter ID</label>
                <input
                  type="number"
                  disabled={!!editingEncounter}
                  value={formData.encounter_id}
                  onChange={(e) => setFormData({ ...formData, encounter_id: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Patient ID Number</label>
                <input
                  type="text"
                  disabled={!!editingEncounter}
                  value={formData.patient_nbr}
                  onChange={(e) => setFormData({ ...formData, patient_nbr: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Medical Specialty</label>
                <input
                  type="text"
                  value={formData.medical_specialty}
                  onChange={(e) => setFormData({ ...formData, medical_specialty: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Days in Hospital</label>
                  <input
                    type="number"
                    value={formData.time_in_hospital}
                    onChange={(e) => setFormData({ ...formData, time_in_hospital: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Number of Lab Procedures</label>
                  <input
                    type="number"
                    value={formData.num_lab_procedures}
                    onChange={(e) => setFormData({ ...formData, num_lab_procedures: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Number of Medications</label>
                  <input
                    type="number"
                    value={formData.num_medications}
                    onChange={(e) => setFormData({ ...formData, num_medications: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Readmission Status</label>
                  <select
                    value={formData.readmitted}
                    onChange={(e) => setFormData({ ...formData, readmitted: e.target.value })}
                  >
                    <option value="NO">NO (No Readmission)</option>
                    <option value=">30">&gt;30 Days</option>
                    <option value="<30">&lt;30 Days</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Encounter</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EncounterList;
