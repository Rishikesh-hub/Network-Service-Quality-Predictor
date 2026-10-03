import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { AlertItem } from '../types';
import { Bell, CheckCircle2, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [activeCount, setActiveCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.getAlerts();
      setAlerts(res.alerts || []);
      setActiveCount(res.active_count || 0);
      setPredictions(res.recent_predictions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Operational Incident Alerts
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Alerts are triggered strictly when model classification satisfies: <b>P(Degraded) &ge; 0.80</b>.
          </p>
        </div>
        <button onClick={fetchAlerts} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }}>
          <RefreshCw size={14} /> Refresh Alerts
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="kpi-card">
          <span className="kpi-title">Active Incident Alerts</span>
          <span className="kpi-value" style={{ color: activeCount > 0 ? 'var(--color-danger)' : 'var(--color-success)' }}>
            {activeCount}
          </span>
          <span className="kpi-sub">{activeCount > 0 ? 'Action required on flagged links' : 'Nominal operations'}</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-title">Decision Threshold</span>
          <span className="kpi-value">80.0%</span>
          <span className="kpi-sub">Optimized for low False Alert Rate</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-title">Alert Policy</span>
          <span className="kpi-value" style={{ fontSize: '18px', paddingTop: '6px' }}>Deduplicated</span>
          <span className="kpi-sub">One active incident per link</span>
        </div>
      </div>

      {/* ACTIVE ALERTS TABLE */}
      <div className="saffron-panel">
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Active Link Incidents (P &ge; 0.80)
        </h3>

        {alerts.length > 0 ? (
          <div className="table-container">
            <table className="nsqp-table">
              <thead>
                <tr>
                  <th>Incident ID</th>
                  <th>Timestamp (UTC)</th>
                  <th>Target Link</th>
                  <th>P(Degraded)</th>
                  <th>Threshold</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => (
                  <tr key={a.id}>
                    <td>#{a.id}</td>
                    <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{a.timestamp.slice(0, 19)}</td>
                    <td style={{ fontWeight: 700, color: 'var(--saffron-primary)' }}>{a.link}</td>
                    <td style={{ fontWeight: 700, color: 'var(--color-danger)' }}>{(a.probability * 100).toFixed(1)}%</td>
                    <td>{(a.threshold * 100).toFixed(0)}%</td>
                    <td>
                      <span className="badge badge-danger">● {a.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ padding: '36px', textAlign: 'center', backgroundColor: 'var(--bg-elevated)', borderRadius: '8px' }}>
            <ShieldCheck size={36} color="var(--color-success)" style={{ margin: '0 auto 8px' }} />
            <h4 style={{ color: 'var(--text-primary)', fontSize: '16px' }}>All Core Links Normal</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
              No telemetry predictions have crossed the 0.80 operational threshold in current logging session.
            </p>
          </div>
        )}
      </div>

      {/* RECENT PREDICTIONS AUDIT LOG */}
      <div className="saffron-panel">
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Recent Prediction Audit Trail (SQLite Repository)
        </h3>

        {predictions.length > 0 ? (
          <div className="table-container">
            <table className="nsqp-table">
              <thead>
                <tr>
                  <th>Audit ID</th>
                  <th>Timestamp</th>
                  <th>Link</th>
                  <th>Probability</th>
                  <th>Classification</th>
                  <th>Model Version</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p) => (
                  <tr key={p.id}>
                    <td>#{p.id}</td>
                    <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{p.timestamp.slice(0, 19)}</td>
                    <td style={{ fontWeight: 600 }}>{p.link}</td>
                    <td>{(p.probability * 100).toFixed(2)}%</td>
                    <td>
                      <span className={`badge ${p.prediction === 1 ? 'badge-danger' : 'badge-online'}`}>
                        {p.status}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{p.model_version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            No prediction logs stored yet. Execute live inferences to populate the audit trail.
          </p>
        )}
      </div>
    </div>
  );
};
