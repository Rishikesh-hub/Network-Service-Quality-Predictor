import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { TelemetryRecord } from '../types';
import { Radio, RefreshCw, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

export const Telemetry: React.FC = () => {
  const [records, setRecords] = useState<TelemetryRecord[]>([]);
  const [links, setLinks] = useState<string[]>([]);
  const [selectedLink, setSelectedLink] = useState<string>('ALL');
  const [stats, setStats] = useState<any>({});
  const [total, setTotal] = useState<number>(0);
  const [offset, setOffset] = useState<number>(0);
  const [limit] = useState<number>(50);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      const res = await api.getTelemetry(selectedLink, limit, offset);
      setRecords(res.records || []);
      setTotal(res.total || 0);
      setStats(res.summary_stats || {});
      setLinks(res.links || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, [selectedLink, offset]);

  const handleLinkChange = (link: string) => {
    setSelectedLink(link);
    setOffset(0);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Telemetry Data Explorer
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Empirical network captures from <code>qos_labeled_cleaned.csv</code> (June 25, 2025 to July 02, 2025).
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="badge badge-sim">◉ SIMULATION MODE</span>
          <button onClick={fetchTelemetry} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {/* FILTER & SUMMARY STATISTICS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {/* Link Filter Card */}
        <div className="saffron-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Filter size={16} color="var(--saffron-primary)" />
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase' }}>
              Filter by Network Link
            </span>
          </div>
          <select
            value={selectedLink}
            onChange={(e) => handleLinkChange(e.target.value)}
            className="form-input"
            style={{ marginTop: '4px' }}
          >
            <option value="ALL">ALL LINKS ({total.toLocaleString()} records)</option>
            {links.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
            Showing records {offset + 1} to {Math.min(offset + limit, total)} of {total.toLocaleString()}
          </span>
        </div>

        {/* Quantile Stats Cards */}
        {stats['rtt'] && (
          <div className="kpi-card">
            <span className="kpi-title">RTT Stats (ms)</span>
            <span className="kpi-value">{stats['rtt'].median} ms</span>
            <span className="kpi-sub">Mean: {stats['rtt'].mean}ms | Max: {stats['rtt'].max}ms</span>
          </div>
        )}
        {stats['packet_loss'] && (
          <div className="kpi-card">
            <span className="kpi-title">Packet Loss Stats</span>
            <span className="kpi-value">{stats['packet_loss'].median}%</span>
            <span className="kpi-sub">Mean: {stats['packet_loss'].mean}% | Max: {stats['packet_loss'].max}%</span>
          </div>
        )}
        {stats['jitter'] && (
          <div className="kpi-card">
            <span className="kpi-title">Jitter Stats (ms)</span>
            <span className="kpi-value">{stats['jitter'].median} ms</span>
            <span className="kpi-sub">Mean: {stats['jitter'].mean}ms | Max: {stats['jitter'].max}ms</span>
          </div>
        )}
      </div>

      {/* TELEMETRY CHART */}
      <div className="saffron-panel">
        <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
          Telemetry Stream Trends ({selectedLink})
        </h4>
        <div style={{ width: '100%', height: '260px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={records} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(58, 42, 22, 0.4)" />
              <XAxis dataKey="datetime" tick={false} stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px' }} />
              <Legend />
              <Line type="monotone" dataKey="rtt" stroke="#F59E0B" name="RTT (ms)" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="jitter" stroke="#38BDF8" name="Jitter (ms)" dot={false} strokeWidth={1.5} />
              <Line type="monotone" dataKey="packet_loss" stroke="#EF4444" name="Packet Loss (%)" dot={false} strokeWidth={1.5} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* DATA TABLE */}
      <div className="saffron-panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Captured Telemetry Records
          </h4>
          {/* Pagination Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0 || loading}
              className="btn-secondary"
              style={{ padding: '4px 8px' }}
            >
              <ChevronLeft size={16} /> Prev
            </button>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit) || 1}
            </span>
            <button
              onClick={() => setOffset(offset + limit)}
              disabled={offset + limit >= total || loading}
              className="btn-secondary"
              style={{ padding: '4px 8px' }}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>

        <div className="table-container">
          <table className="nsqp-table">
            <thead>
              <tr>
                <th>Timestamp (UTC)</th>
                <th>Link</th>
                <th>Loss (%)</th>
                <th>Jitter (ms)</th>
                <th>RTT (ms)</th>
                <th>Outflow (Mbps)</th>
                <th>Inflow (Mbps)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {r.datetime ? r.datetime.slice(0, 19) : r.timestamp}
                  </td>
                  <td style={{ fontWeight: 700, color: 'var(--saffron-primary)' }}>{r.link}</td>
                  <td>{r.packet_loss}</td>
                  <td>{r.jitter}</td>
                  <td>{r.rtt}</td>
                  <td>{r.outflow_Router}</td>
                  <td>{r.inflow_Router}</td>
                  <td>
                    {r.degradation === 1 ? (
                      <span className="badge badge-danger">DEGRADED</span>
                    ) : (
                      <span className="badge badge-online">NORMAL</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
