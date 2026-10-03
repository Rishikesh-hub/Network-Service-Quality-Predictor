import React, { useState } from 'react';
import { api } from '../api/client';
import { PredictionRequest, PredictionResponse } from '../types';
import { Zap, CheckCircle2, AlertTriangle, ArrowUpRight, ArrowDownRight, Minus, RefreshCw, Layers } from 'lucide-react';

const EXPECTED_LINKS = [
  'R1-R2', 'R1-R9', 'R2-R3', 'R2-R9', 'R3-R4', 'R3-R8',
  'R4-R5', 'R4-R6', 'R6-R5', 'R7-R6', 'R8-R6', 'R8-R7', 'R9-R8'
];

export const Prediction: React.FC = () => {
  const [formData, setFormData] = useState<PredictionRequest>({
    packet_loss: 0.0,
    jitter: 0.12,
    rtt: 1.2,
    outflow_Router: 4.65,
    inflow_Router: 4.65,
    resolve: 0.03,
    ttl: 62.0,
    probe_duration: 0.0,
    link: 'R1-R9',
  });

  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof PredictionRequest, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: field === 'link' ? value : parseFloat(value) || 0.0,
    }));
  };

  const applyPreset = (presetName: string) => {
    if (presetName === 'nominal') {
      setFormData({
        packet_loss: 0.0,
        jitter: 0.12,
        rtt: 1.2,
        outflow_Router: 4.65,
        inflow_Router: 4.65,
        resolve: 0.03,
        ttl: 62.0,
        probe_duration: 0.0,
        link: 'R1-R9',
      });
    } else if (presetName === 'loss') {
      setFormData({
        packet_loss: 5.0,
        jitter: 0.12,
        rtt: 1.2,
        outflow_Router: 4.65,
        inflow_Router: 4.65,
        resolve: 0.03,
        ttl: 62.0,
        probe_duration: 0.0,
        link: 'R1-R9',
      });
    } else if (presetName === 'rtt') {
      setFormData({
        packet_loss: 0.0,
        jitter: 0.12,
        rtt: 35.0,
        outflow_Router: 4.65,
        inflow_Router: 4.65,
        resolve: 0.03,
        ttl: 62.0,
        probe_duration: 0.0,
        link: 'R1-R9',
      });
    } else if (presetName === 'multi') {
      setFormData({
        packet_loss: 4.0,
        jitter: 2.5,
        rtt: 28.0,
        outflow_Router: 20.0,
        inflow_Router: 20.0,
        resolve: 0.04,
        ttl: 62.0,
        probe_duration: 0.02,
        link: 'R1-R9',
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.predictQoS(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Inference execution failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const isDegraded = result?.status === 'DEGRADED';
  const probPercent = result ? (result.probability * 100).toFixed(2) : '0.00';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title & Presets Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Real-Time QoS Inference Workspace
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Transform 9 raw operational metrics into the strict 26-feature ANN representation.
          </p>
        </div>

        {/* Demo Presets */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>DEMO PRESETS:</span>
          <button type="button" onClick={() => applyPreset('nominal')} className="btn-secondary" style={{ fontSize: '12px', padding: '6px 12px' }}>
            Nominal
          </button>
          <button type="button" onClick={() => applyPreset('loss')} className="btn-secondary" style={{ fontSize: '12px', padding: '6px 12px' }}>
            High Loss (5%)
          </button>
          <button type="button" onClick={() => applyPreset('rtt')} className="btn-secondary" style={{ fontSize: '12px', padding: '6px 12px' }}>
            High Latency (35ms)
          </button>
          <button type="button" onClick={() => applyPreset('multi')} className="btn-secondary" style={{ fontSize: '12px', padding: '6px 12px' }}>
            Multi-Vector
          </button>
        </div>
      </div>

      {/* Main Grid: Form Left, Results Right */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '24px' }}>
        {/* INPUT FORM */}
        <div className="saffron-panel">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* GROUP 1: NETWORK QUALITY */}
            <div>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--saffron-primary)', textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: '12px' }}>
                1. Network Impairments (QoS)
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Packet Loss (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={formData.packet_loss}
                    onChange={(e) => handleChange('packet_loss', e.target.value)}
                    className="form-input"
                    required
                  />
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Nominal: 0.0% | Degraded: ~0.64%</span>
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Packet Jitter (ms)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.jitter}
                    onChange={(e) => handleChange('jitter', e.target.value)}
                    className="form-input"
                    required
                  />
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Nominal: 0.12ms | Degraded: ~2.18ms</span>
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Round Trip Time (RTT) (ms)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    value={formData.rtt}
                    onChange={(e) => handleChange('rtt', e.target.value)}
                    className="form-input"
                    required
                  />
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Nominal: 1.2ms | Degraded: ~18.98ms</span>
                </div>
              </div>
            </div>

            <hr style={{ borderColor: 'var(--border-color)', opacity: 0.6 }} />

            {/* GROUP 2: TRAFFIC */}
            <div>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--saffron-primary)', textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: '12px' }}>
                2. Flow Router Throughput
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Outflow Router (Mbps)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    value={formData.outflow_Router}
                    onChange={(e) => handleChange('outflow_Router', e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Inflow Router (Mbps)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    value={formData.inflow_Router}
                    onChange={(e) => handleChange('inflow_Router', e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
              </div>
            </div>

            <hr style={{ borderColor: 'var(--border-color)', opacity: 0.6 }} />

            {/* GROUP 3: PROBE / ROUTING */}
            <div>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--saffron-primary)', textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: '12px' }}>
                3. Probe & Routing Topology
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    DNS Resolve Time (s)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.resolve}
                    onChange={(e) => handleChange('resolve', e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    TTL Value
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="1"
                    max="255"
                    value={formData.ttl}
                    onChange={(e) => handleChange('ttl', e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Probe Duration (s)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.probe_duration}
                    onChange={(e) => handleChange('probe_duration', e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                    Core Network Link
                  </label>
                  <select
                    value={formData.link}
                    onChange={(e) => handleChange('link', e.target.value)}
                    className="form-input"
                  >
                    {EXPECTED_LINKS.map((l) => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <button type="submit" className="btn-saffron" disabled={loading} style={{ justifyContent: 'center', marginTop: '10px' }}>
              {loading ? <RefreshCw size={18} className="spin-icon" /> : <Zap size={18} />}
              {loading ? 'Executing ANN Pipeline...' : 'RUN QOS PREDICTION'}
            </button>
          </form>
        </div>

        {/* INFERENCE OUTPUT PANEL */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {error && (
            <div className="saffron-panel" style={{ borderColor: 'var(--color-danger)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-danger)', marginBottom: '8px' }}>
                <AlertTriangle size={20} />
                <h4 style={{ fontWeight: 700 }}>Prediction Error</h4>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{error}</p>
            </div>
          )}

          {result ? (
            <div className="saffron-panel" style={{ borderColor: isDegraded ? 'var(--color-danger)' : 'var(--color-success)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <span className={`badge ${isDegraded ? 'badge-danger' : 'badge-online'}`} style={{ fontSize: '14px', padding: '6px 14px' }}>
                  {isDegraded ? '! DEGRADED QoS' : '✓ NORMAL QoS'}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Audit ID: #{result.prediction_id || 'LOCAL'}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div className="kpi-card" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                  <span className="kpi-title">P(Degraded)</span>
                  <span className="kpi-value" style={{ color: isDegraded ? 'var(--color-danger)' : 'var(--color-success)' }}>
                    {probPercent}%
                  </span>
                </div>
                <div className="kpi-card" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                  <span className="kpi-title">Threshold</span>
                  <span className="kpi-value">{(result.threshold * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* Progress visual */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ height: '8px', backgroundColor: 'var(--bg-elevated)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${Math.min(100, Math.max(0, Number(probPercent)))}%`,
                      height: '100%',
                      backgroundColor: isDegraded ? 'var(--color-danger)' : 'var(--color-success)',
                    }}
                  />
                </div>
              </div>

              <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
                Top Contributing Signals
              </h4>
              <div className="table-container">
                <table className="nsqp-table">
                  <thead>
                    <tr>
                      <th>Measurement</th>
                      <th>Score</th>
                      <th>Direction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.contributors.map((c, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: 600 }}>{c.feature}</td>
                        <td>{c.importance_score.toFixed(4)}</td>
                        <td>
                          <span
                            style={{
                              color:
                                c.direction === 'risk_up'
                                  ? 'var(--color-danger)'
                                  : c.direction === 'risk_down'
                                  ? 'var(--color-success)'
                                  : 'var(--text-secondary)',
                              fontWeight: 600,
                              fontSize: '12px',
                            }}
                          >
                            {c.direction}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="saffron-panel" style={{ textAlign: 'center', padding: '60px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <Layers size={48} color="var(--text-muted)" style={{ marginBottom: '16px' }} />
              <h4 style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>Inference Engine Ready</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px', maxWidth: '340px', marginTop: '6px' }}>
                Enter operational telemetry values on the left or select a preset and click <b>RUN QOS PREDICTION</b>.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
