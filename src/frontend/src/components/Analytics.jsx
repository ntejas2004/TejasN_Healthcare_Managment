import React, { useEffect, useState } from 'react';
import { getDemographicsStats, getReadmissionStats, getLengthOfStayStats } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Analytics = () => {
  const [demographics, setDemographics] = useState({ race: [], gender: [] });
  const [readmissions, setReadmissions] = useState([]);
  const [stayStats, setStayStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [demoData, readmData, stayData] = await Promise.all([
          getDemographicsStats(),
          getReadmissionStats(),
          getLengthOfStayStats()
        ]);
        setDemographics(demoData);
        setReadmissions(readmData);
        setStayStats(stayData);
      } catch (err) {
        console.error('Failed to load analytics charts:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

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
    </div>
  );
};

export default Analytics;
