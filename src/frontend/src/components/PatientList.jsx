import React, { useEffect, useState } from 'react';
import { getPatients, createPatient, updatePatient, deletePatient } from '../api/client';
import { Plus, Search, Trash2, Edit, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const PatientList = () => {
  const { canEdit, canDelete } = useAuth();
  const [patients, setPatients] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [editingPatient, setEditingPatient] = useState(null);
  const [formData, setFormData] = useState({
    patient_nbr: '',
    race: 'Caucasian',
    gender: 'Female',
    age: '[60-70)',
    weight: 'Unknown'
  });

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const data = await getPatients(page, 15, search);
      setPatients(data.data);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch patients:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [page, search]);

  const handleOpenCreate = () => {
    setEditingPatient(null);
    setFormData({
      patient_nbr: Math.floor(10000000 + Math.random() * 90000000).toString(),
      race: 'Caucasian',
      gender: 'Female',
      age: '[60-70)',
      weight: 'Unknown'
    });
    setShowModal(true);
  };

  const handleOpenEdit = (patient) => {
    setEditingPatient(patient);
    setFormData({
      patient_nbr: patient.patient_nbr,
      race: patient.race || 'Unknown',
      gender: patient.gender || 'Unknown',
      age: patient.age || 'Unknown',
      weight: patient.weight || 'Unknown'
    });
    setShowModal(true);
  };

  const handleDelete = async (patientNbr) => {
    if (window.confirm(`Are you sure you want to delete patient '${patientNbr}'?`)) {
      try {
        await deletePatient(patientNbr);
        fetchPatients();
      } catch (err) {
        alert('Error deleting patient');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingPatient) {
        await updatePatient(editingPatient.patient_nbr, {
          race: formData.race,
          gender: formData.gender,
          age: formData.age,
          weight: formData.weight
        });
      } else {
        await createPatient(formData);
      }
      setShowModal(false);
      fetchPatients();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error saving patient record');
    }
  };

  return (
    <div className="table-card">
      <div className="table-header">
        <div>
          <h2 className="table-title">Patient Records Management</h2>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
            Showing {patients.length} of {total.toLocaleString()} patients
          </span>
        </div>

        <div className="table-actions">
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search by Patient ID, Race, Gender..."
              className="input-search"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              style={{ paddingLeft: '2.2rem', width: '280px' }}
            />
            <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
          </div>

          {canEdit && (
            <button className="btn-primary" onClick={handleOpenCreate}>
              <Plus size={16} /> Add Patient
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Patients...</div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Patient Number</th>
                <th>Race / Ethnicity</th>
                <th>Gender</th>
                <th>Age Bracket</th>
                <th>Weight Range</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((pt) => (
                <tr key={pt.patient_nbr}>
                  <td><strong>{pt.patient_nbr}</strong></td>
                  <td>{pt.race || 'Unknown'}</td>
                  <td>{pt.gender || 'Unknown'}</td>
                  <td>{pt.age || 'Unknown'}</td>
                  <td>{pt.weight || 'Unknown'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {canEdit && (
                        <button className="btn-secondary" onClick={() => handleOpenEdit(pt)}>
                          <Edit size={14} /> Edit
                        </button>
                      )}
                      {canDelete && (
                        <button className="btn-danger" onClick={() => handleDelete(pt.patient_nbr)}>
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

      {/* Create / Edit Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingPatient ? 'Edit Patient Record' : 'Create New Patient'}</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Patient ID Number</label>
                <input
                  type="text"
                  disabled={!!editingPatient}
                  value={formData.patient_nbr}
                  onChange={(e) => setFormData({ ...formData, patient_nbr: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Race / Ethnicity</label>
                <select
                  value={formData.race}
                  onChange={(e) => setFormData({ ...formData, race: e.target.value })}
                >
                  <option value="Caucasian">Caucasian</option>
                  <option value="AfricanAmerican">AfricanAmerican</option>
                  <option value="Hispanic">Hispanic</option>
                  <option value="Asian">Asian</option>
                  <option value="Other">Other</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>

              <div className="form-group">
                <label>Gender</label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                >
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>

              <div className="form-group">
                <label>Age Group</label>
                <select
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                >
                  <option value="[0-10)">[0-10)</option>
                  <option value="[10-20)">[10-20)</option>
                  <option value="[20-30)">[20-30)</option>
                  <option value="[30-40)">[30-40)</option>
                  <option value="[40-50)">[40-50)</option>
                  <option value="[50-60)">[50-60)</option>
                  <option value="[60-70)">[60-70)</option>
                  <option value="[70-80)">[70-80)</option>
                  <option value="[80-90)">[80-90)</option>
                  <option value="[90-100)">[90-100)</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Patient</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientList;
