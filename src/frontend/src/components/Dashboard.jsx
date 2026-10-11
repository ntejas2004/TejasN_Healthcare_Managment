import React, { useEffect, useState } from 'react';
import { Users, FileText, AlertCircle, Clock, Pill, TestTube } from 'lucide-react';
import { getAnalyticsSummary, getReadmissionStats, getLengthOfStayStats } from '../api/client';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [readmissions, setReadmissions] = useState([]);
  const [stayStats, setStayStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumData, readmData, stayData] = await Promise.all([
          getAnalyticsSummary(),
          getReadmissionStats(),
          getLengthOfStayStats()
        ]);
        setSummary(sumData);
        setReadmissions(readmData);
        setStayStats(stayData);
      } catch (err) {
        console.error('Error fetching dashboard analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Healthcare Analytics...</div>;
  }

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: '700' }}>Healthcare Executive Dashboard</h2>
      
      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon"><Users size={24} /></div>
          <div>
            <div className="kpi-title">Total Patients</div>
            <div className="kpi-value">{summary?.total_patients?.toLocaleString()}</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#e0e7ff', color: '#4338ca' }}><FileText size={24} /></div>
          <div>
            <div className="kpi-title">Total Encounters</div>
            <div className="kpi-value">{summary?.total_encounters?.toLocaleString()}</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#fef3c7', color: '#d97706' }}><AlertCircle size={24} /></div>
          <div>
            <div className="kpi-title">Readmission Rate</div>
            <div className="kpi-value">{summary?.readmission_rate_pct}%</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#dcfce7', color: '#15803d' }}><Clock size={24} /></div>
          <div>
            <div className="kpi-title">Avg Length of Stay</div>
            <div className="kpi-value">{summary?.avg_length_of_stay_days} Days</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#f3e8ff', color: '#7e22ce' }}><Pill size={24} /></div>
          <div>
            <div className="kpi-title">Avg Medications</div>
            <div className="kpi-value">{summary?.avg_num_medications}</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#ccfbf1', color: '#0f766e' }}><TestTube size={24} /></div>
          <div>
            <div className="kpi-title">Avg Lab Procedures</div>
            <div className="kpi-value">{summary?.avg_lab_procedures}</div>
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-title">Hospital Readmission Breakdown</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={readmissions}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="count"
                  nameKey="category"
                  label={({ category, percentage }) => `${category}: ${percentage}%`}
                >
                  {readmissions.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-title">Length of Hospital Stay (Days)</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stayStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="days" label={{ value: 'Days in Hospital', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Encounters', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Bar dataKey="count" fill="#0284c7" name="Encounters" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
