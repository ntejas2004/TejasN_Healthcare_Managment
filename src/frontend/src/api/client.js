import axios from 'axios';

// API base client connecting to FastAPI backend
const API_BASE_URL = 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Attach JWT token on every request ────────────────────────────────────────
client.interceptors.request.use((config) => {
  const stored = localStorage.getItem('hpms_user');
  if (stored) {
    try {
      const { access_token } = JSON.parse(stored);
      if (access_token) config.headers.Authorization = `Bearer ${access_token}`;
    } catch (_) {}
  }
  return config;
});

// ── Analytics ─────────────────────────────────────────────────────────────────
export const getAnalyticsSummary = async () => {
  const response = await client.get('/analytics/summary');
  return response.data;
};

export const getReadmissionStats = async () => {
  const response = await client.get('/analytics/readmissions');
  return response.data;
};

export const getLengthOfStayStats = async () => {
  const response = await client.get('/analytics/length-of-stay');
  return response.data;
};

export const getDemographicsStats = async () => {
  const response = await client.get('/analytics/demographics');
  return response.data;
};

// ── Patients ──────────────────────────────────────────────────────────────────
export const getPatients = async (page = 1, limit = 15, search = '') => {
  const params = { page, limit };
  if (search) params.search = search;
  const response = await client.get('/patients', { params });
  return response.data;
};

export const getPatient = async (patientNbr) => {
  const response = await client.get(`/patients/${patientNbr}`);
  return response.data;
};

export const createPatient = async (patientData) => {
  const response = await client.post('/patients', patientData);
  return response.data;
};

export const updatePatient = async (patientNbr, patientData) => {
  const response = await client.put(`/patients/${patientNbr}`, patientData);
  return response.data;
};

export const deletePatient = async (patientNbr) => {
  const response = await client.delete(`/patients/${patientNbr}`);
  return response.data;
};

// ── Encounters ────────────────────────────────────────────────────────────────
export const getEncounters = async (page = 1, limit = 15, search = '', readmitted = '') => {
  const params = { page, limit };
  if (search) params.search = search;
  if (readmitted) params.readmitted = readmitted;
  const response = await client.get('/encounters', { params });
  return response.data;
};

export const getEncounter = async (encounterId) => {
  const response = await client.get(`/encounters/${encounterId}`);
  return response.data;
};

export const createEncounter = async (encounterData) => {
  const response = await client.post('/encounters', encounterData);
  return response.data;
};

export const updateEncounter = async (encounterId, encounterData) => {
  const response = await client.put(`/encounters/${encounterId}`, encounterData);
  return response.data;
};

export const deleteEncounter = async (encounterId) => {
  const response = await client.delete(`/encounters/${encounterId}`);
  return response.data;
};

export default client;
