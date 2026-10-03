import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { PredictionResponse, AlertItem, TelemetryRecord } from '../types';
import { CheckCircle2, AlertTriangle, Activity, ArrowUpRight, ArrowDownRight, Minus, RefreshCw } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

export const Dashboard: React.FC = () => {
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Initial baseline nominal prediction
      const nominalPayload = {
        packet_loss: 0.0,
        jitter: 0.12,
        rtt: 1.2,
        outflow_Router: 4.65,
        inflow_Router: 4.65,
        resolve: 0.03,
        ttl: 62.0,
        probe_duration: 0.0,
        link: 'R1-R9',
      };
      const predRes = await api.predictQoS(nominalPayload);
      setPrediction(predRes);

      // 2. Alerts
      const alertsRes = await api.getAlerts('ACTIVE', 5);
      setAlerts(alertsRes.alerts || []);

      // 3. Telemetry for trend chart
      const telemRes = await api.getTelemetry('ALL', 80, 0);
      setTelemetry(telemRes.records || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading && !prediction) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-secondary)' }}>
        <RefreshCw size={36} className="spin-icon" style={{ animation: 'spin 1.5s linear infinite' }} />
        <p style={{ marginTop: '16px', fontSize: '16px' }}>Connecting to NSQP Inference Engine (:8000)...</p>
        <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error && !prediction) {
    return (
      <div className="saffron-panel" style={{ borderColor: 'var(--color-danger)', textAlign: 'center', padding: '40px' }}>
        <AlertTriangle size={48} color="var(--color-danger)" style={{ margin: '0 auto 16px' }} />
        <h3 style={{ color: 'var(--color-danger)', fontSize: '20px' }}>API Connection Error</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>{error}</p>
        <button onClick={fetchDashboardData} className="btn-saffron" style={{ marginTop: '20px' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const isDegraded = prediction?.status === 'DEGRADED';
  const probPercent = prediction ? (prediction.probability * 100).toFixed(2) : '0.00';
  const thresholdPercent = prediction ? (prediction.threshold * 100).toFixed(0) : '80';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 1. PRIMARY STATUS BANNER CARD */}
      <div
        style={{
          backgroundColor: isDegraded ? 'rgba(239, 68, 68, 0.08)' : 'rgba(34, 197, 94, 0.08)',
          border: `2px solid ${isDegraded ? 'var(--color-danger)' : 'var(--color-success)'}`,
          borderRadius: '16px',
          padding: '28px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          boxShadow: isDegraded ? '0 0 25px rgba(239, 68, 68, 0.2)' : '0 0 25px rgba(34, 197, 94, 0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          {isDegraded ? (
            <AlertTriangle size={36} color="var(--color-danger)" />
          ) : (
            <CheckCircle2 size={36} color="var(--color-success)" />
          )}
          <h2
            style={{
              fontSize: '34px',
              fontWeight: 900,
              letterSpacing: '1px',
              color: isDegraded ? 'var(--color-danger)' : 'var(--color-success)',
              margin: 0,
            }}
          >
            {isDegraded ? '! DEGRADED QoS ALERT' : '✓ NORMAL QoS STATUS'}
          </h2>
        </div>

        <p style={{ fontSize: '18px', color: 'var(--text-primary)', marginTop: '6px' }}>
          Degradation Probability: <b style={{ color: 'var(--saffron-primary)' }}>{probPercent}%</b> &nbsp;|&nbsp; Operating Decision Threshold: <b>{thresholdPercent}%</b>
        </p>

        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
          Classification Mode: <b>Current-State Evaluation</b> &bull; Model: <b>MLP / ANN (128, 64)</b> &bull; Evaluation Split: Untouched Test ($F_1 = 0.9648$)
        </p>

        {/* Probability Gauge Bar */}
        <div style={{ width: '100%', maxWidth: '640px', marginTop: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
            <span>0% (Safe)</span>
            <span style={{ color: 'var(--saffron-primary)', fontWeight: 700 }}>Threshold: 80%</span>
            <span>100% (Critical)</span>
          </div>
          <div style={{ position: 'relative', height: '14px', backgroundColor: 'var(--bg-elevated)', borderRadius: '7px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${Math.min(100, Math.max(0, Number(probPercent)))}%`,
                height: '100%',
                backgroundColor: isDegraded ? 'var(--color-danger)' : 'var(--color-success)',
                transition: 'width 0.4s ease',
              }}
            />
            {/* Threshold Line Indicator at 80% */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                bottom: 0,
                left: '80%',
                width: '3px',
                backgroundColor: 'var(--saffron-primary)',
                boxShadow: '0 0 6px var(--saffron-primary)',
              }}
            />
          </div>
        </div>
      </div>

      {/* 2. KPI METRICS CARDS */}
      <div>
        <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '14px' }}>
          Instantaneous Telemetry Observations (Nominal Sample)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div className="kpi-card">
            <span className="kpi-title">Packet Loss</span>
            <span className="kpi-value">{prediction?.telemetry?.packet_loss ?? 0.0}%</span>
            <span className="kpi-sub">Nominal median: 0.0%</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-title">Jitter</span>
            <span className="kpi-value">{prediction?.telemetry?.jitter ?? 0.12} ms</span>
            <span className="kpi-sub">Nominal median: 0.12 ms</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-title">Round Trip Time (RTT)</span>
            <span className="kpi-value">{prediction?.telemetry?.rtt ?? 1.2} ms</span>
            <span className="kpi-sub">Nominal median: 1.2 ms</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-title">Outflow Router</span>
            <span className="kpi-value">{prediction?.telemetry?.outflow_Router ?? 4.65} Mbps</span>
            <span className="kpi-sub">Flow egress rate</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-title">Inflow Router</span>
            <span className="kpi-value">{prediction?.telemetry?.inflow_Router ?? 4.65} Mbps</span>
            <span className="kpi-sub">Flow ingress rate</span>
          </div>
        </div>
      </div>

      {/* 3. CONTRIBUTING MEASUREMENTS + ACTIVE ALERTS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        {/* Contributors Panel */}
        <div className="saffron-panel">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Important Contributing Measurements
            </h4>
            <span className="badge badge-sim">RANDOM FOREST IMPORTANCE</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Statistical feature rankings from reference Random Forest model. Explanatory evidence only, <b>NOT causal root cause</b>.
          </p>

          <div className="table-container">
            <table className="nsqp-table">
              <thead>
                <tr>
                  <th>Measurement</th>
                  <th>Relative Score</th>
                  <th>Signal Direction</th>
                </tr>
              </thead>
              <tbody>
                {prediction?.contributors?.map((c, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{c.feature}</td>
                    <td>{c.importance_score.toFixed(4)}</td>
                    <td>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          color:
                            c.direction === 'risk_up'
                              ? 'var(--color-danger)'
                              : c.direction === 'risk_down'
                              ? 'var(--color-success)'
                              : 'var(--text-secondary)',
                          fontSize: '12px',
                          fontWeight: 600,
                        }}
                      >
                        {c.direction === 'risk_up' ? (
                          <ArrowUpRight size={14} />
                        ) : c.direction === 'risk_down' ? (
                          <ArrowDownRight size={14} />
                        ) : (
                          <Minus size={14} />
                        )}
                        {c.direction}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Alerts Panel */}
        <div className="saffron-panel">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Active Incident Alerts
            </h4>
            <span className="badge badge-danger">THRESHOLD &ge; 0.80</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Persistent operational alerts recorded in SQLite database.
          </p>

          {alerts.length > 0 ? (
            <div className="table-container">
              <table className="nsqp-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Link</th>
                    <th>P(Degraded)</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((a) => (
                    <tr key={a.id}>
                      <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{a.timestamp.slice(0, 19)}</td>
                      <td style={{ fontWeight: 700, color: 'var(--saffron-primary)' }}>{a.link}</td>
                      <td>{(a.probability * 100).toFixed(1)}%</td>
                      <td><span className="badge badge-danger">● ACTIVE</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ padding: '36px', textAlign: 'center', backgroundColor: 'var(--bg-elevated)', borderRadius: '8px' }}>
              <CheckCircle2 size={32} color="var(--color-success)" style={{ margin: '0 auto 8px' }} />
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                No active degradation alerts recorded in database. All links operating within nominal limits.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 4. HISTORICAL TELEMETRY TRENDS */}
      <div className="saffron-panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Historical Telemetry Trends (Replay Stream)
            </h4>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Chronologically sampled records from <code>qos_labeled_cleaned.csv</code>
            </p>
          </div>
          <span className="badge badge-sim">◉ SIMULATION MODE</span>
        </div>

        {telemetry.length > 0 ? (
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetry} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(58, 42, 22, 0.4)" />
                <XAxis dataKey="datetime" tick={false} stroke="var(--text-muted)" />
                <YAxis stroke="var(--text-muted)" fontSize={12} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)' }}
                />
                <Legend />
                <Line type="monotone" dataKey="rtt" stroke="#F59E0B" name="RTT (ms)" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="jitter" stroke="#38BDF8" name="Jitter (ms)" dot={false} strokeWidth={1.5} />
                <Line type="monotone" dataKey="packet_loss" stroke="#EF4444" name="Packet Loss (%)" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)' }}>No telemetry trend data available.</p>
        )}
      </div>
    </div>
  );
};
