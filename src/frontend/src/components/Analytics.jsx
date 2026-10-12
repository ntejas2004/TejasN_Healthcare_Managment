import React, { useEffect, useState } from 'react';
import { getDemographicsStats, getReadmissionStats, getLengthOfStayStats, getScheduledReports, triggerScheduledReport } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Play, Calendar, CheckCircle2, RefreshCw } from 'lucide-react';

const Analytics = () => {
  const [demographics, setDemographics] = useState({ race: [], gender: [] });
  const [readmissions, setReadmissions] = useState([]);
  const [stayStats, setStayStats] = useState([]);
  const [scheduledReports, setScheduledReports] = useState([]);
  const [triggering, setTriggering] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    try {
      const reports = await getScheduledReports();
      setScheduledReports(reports || []);
    } catch (err) {
      console.error('Failed to load scheduled reports:', err);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [demoData, readmData, stayData, reports] = await Promise.all([
          getDemographicsStats(),
          getReadmissionStats(),
          getLengthOfStayStats(),
          getScheduledReports()
        ]);
        setDemographics(demoData);
        setReadmissions(readmData);
        setStayStats(stayData);
        setScheduledReports(reports || []);
      } catch (err) {
        console.error('Failed to load analytics charts:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleTriggerReport = async () => {
    setTriggering(true);
    try {
      await triggerScheduledReport();
      await fetchReports();
    } catch (err) {
      console.error('Failed to trigger report:', err);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Advanced Healthcare Analytics...</div>;
  }

  const COLORS = ['#0284c7', '#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#cbd5e1'];

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: '700' }}>Healthcare Operational Analytics</h2>

      <div className="charts-grid">
        {/* Race Distribution Chart */}
        <div className="chart-card">
          <div className="chart-title">Patient Demographics by Race / Ethnicity</div>
          <div style={{ height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={demographics.race} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="category" type="category" width={120} />
                <Tooltip />
                <Bar dataKey="count" fill="#0284c7" name="Patients" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gender Distribution Chart */}
        <div className="chart-card">
          <div className="chart-title">Patient Gender Distribution</div>
          <div style={{ height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={demographics.gender}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="count"
                  nameKey="category"
                  label={({ category, count }) => `${category}: ${count.toLocaleString()}`}
                >
                  {demographics.gender.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Length of Stay Histogram */}
        <div className="chart-card" style={{ gridColumn: '1 / -1' }}>
          <div className="chart-title">Length of Stay Breakdown across Hospital Encounters</div>
          <div style={{ height: '350px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stayStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="days" label={{ value: 'Days in Hospital (1 to 14 Days)', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Number of Encounters', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" name="Encounters" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Scheduled Reporting History Section */}
      <div style={{ marginTop: '2.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Calendar size={20} color="#0d9488" /> Automated Scheduled Clinical Reports
            </h3>
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', margin: '0.25rem 0 0 0' }}>
              Generated every 24 hours by the background reporting scheduler (APScheduler).
            </p>
          </div>
          <button
            className="btn-primary"
            onClick={handleTriggerReport}
            disabled={triggering}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {triggering ? <RefreshCw size={15} className="spin" /> : <Play size={15} />}
            {triggering ? 'Generating Report...' : 'Trigger Report Now'}
          </button>
        </div>

        {scheduledReports.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b', background: '#1e293b', borderRadius: '8px' }}>
            No scheduled reports generated yet. Click "Trigger Report Now" to run an immediate aggregation.
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Generated At</th>
                  <th>Report Name</th>
                  <th>Total Patients</th>
                  <th>Total Encounters</th>
                  <th>Readmission Rate</th>
                  <th>Avg Length of Stay</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {scheduledReports.map((report, idx) => (
                  <tr key={idx}>
                    <td><strong>{report.timestamp}</strong></td>
                    <td>{report.report_name}</td>
                    <td>{report.total_patients?.toLocaleString()}</td>
                    <td>{report.total_encounters?.toLocaleString()}</td>
                    <td>
                      <span style={{ color: '#0d9488', fontWeight: '600' }}>
                        {report.readmission_rate_pct}%
                      </span>
                    </td>
                    <td>{report.avg_length_of_stay_days} days</td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', color: '#10b981', fontWeight: '600', fontSize: '0.85rem' }}>
                        <CheckCircle2 size={15} /> {report.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;
