import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { MetricsResponse, ModelMetadata } from '../types';
import { BarChart3, CheckCircle2, Sliders, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

export const ModelPerformance: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [modelMeta, setModelMeta] = useState<ModelMetadata | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([api.getMetrics(), api.getModelMetadata()])
      .then(([m, meta]) => {
        setMetrics(m);
        setModelMeta(meta);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
          Model Architecture & Evaluated Benchmarks
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Official stored evaluation results on the chronologically split, untouched test dataset.
        </p>
      </div>

      {/* TOP ROW: OFFICIAL EVALUATION KPIS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="kpi-card" style={{ borderColor: 'var(--saffron-primary)' }}>
          <span className="kpi-title" style={{ color: 'var(--saffron-primary)' }}>Final Test F1-Score</span>
          <span className="kpi-value" style={{ color: 'var(--saffron-primary)' }}>0.9648</span>
          <span className="kpi-sub">Operating threshold: 0.80</span>
        </div>
        <div className="kpi-card" style={{ borderColor: 'var(--color-success)' }}>
          <span className="kpi-title" style={{ color: 'var(--color-success)' }}>Final Test False Alert Rate</span>
          <span className="kpi-value" style={{ color: 'var(--color-success)' }}>1.1805%</span>
          <span className="kpi-sub">FAR = FP / (FP + TN)</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-title">Validation F1-Score</span>
          <span className="kpi-value">0.9511</span>
          <span className="kpi-sub">Optimal validation threshold peak</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-title">Validation False Alert Rate</span>
          <span className="kpi-value">1.0488%</span>
          <span className="kpi-sub">Tuned on validation split</span>
        </div>
      </div>

      {/* MODEL SPECIFICATION & THRESHOLD BANNER */}
      <div className="saffron-panel" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div>
          <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
            Neural Network Configuration
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Model Type:</span>
              <b>sklearn.neural_network.MLPClassifier</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Hidden Layer Structure:</span>
              <b style={{ color: 'var(--saffron-primary)' }}>(128, 64) Neurons</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Activation Function:</span>
              <b>ReLU (Rectified Linear Unit)</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Optimizer / Solver:</span>
              <b>Adam (lr_init=0.001)</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>L2 Regularization (&alpha;):</span>
              <b>0.001</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Early Stopping:</span>
              <b>Enabled (patience=10)</b>
            </div>
          </div>
        </div>

        <div>
          <h4 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
            Operational Decision Policy
          </h4>
          <div style={{ padding: '16px', backgroundColor: 'var(--bg-elevated)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--saffron-primary)' }}>OFFICIAL OPERATING THRESHOLD</span>
              <span className="badge badge-sim">0.80</span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              The decision rule is strictly defined as <code>prediction = int(P(Degraded) &ge; 0.80)</code>. This was selected based on validation set F1 maximization to suppress false alerts under normal bursty campus network traffic.
            </p>
            <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
              <span className="badge badge-online">P &lt; 0.80 &rarr; NORMAL (0)</span>
              <span className="badge badge-danger">P &ge; 0.80 &rarr; DEGRADED (1)</span>
            </div>
          </div>
        </div>
      </div>

      {/* COMPARATIVE BENCHMARK MATRIX */}
      <div className="saffron-panel">
        <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Comparative Experimental Benchmark Matrix
        </h4>
        <div className="table-container">
          <table className="nsqp-table">
            <thead>
              <tr>
                <th>Model Experiment</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>False Alert Rate</th>
                <th>Threshold</th>
              </tr>
            </thead>
            <tbody>
              {metrics?.benchmarks?.map((b, i) => (
                <tr key={i} style={{ backgroundColor: b.model.includes('Tuned Optimal') ? 'rgba(245, 158, 11, 0.05)' : undefined }}>
                  <td style={{ fontWeight: 700, color: b.model.includes('Tuned Optimal') ? 'var(--saffron-primary)' : 'var(--text-primary)' }}>
                    {b.model}
                  </td>
                  <td>{b.precision}</td>
                  <td>{b.recall}</td>
                  <td style={{ fontWeight: 700 }}>{b.f1}</td>
                  <td style={{ color: b.far.startsWith('0.') || b.far.startsWith('1.') ? 'var(--color-success)' : 'var(--color-danger)' }}>
                    {b.far}
                  </td>
                  <td>{b.threshold.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* THRESHOLD TUNING TRAJECTORY CHART */}
      {metrics?.threshold_curve && (
        <div className="saffron-panel">
          <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
            Validation Threshold Sweep Trajectory (0.20 to 0.80)
          </h4>
          <div style={{ width: '100%', height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.threshold_curve} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(58, 42, 22, 0.4)" />
                <XAxis dataKey="threshold" stroke="var(--text-muted)" />
                <YAxis stroke="var(--text-muted)" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px' }} />
                <Legend />
                <Line type="monotone" dataKey="f1" stroke="#F59E0B" name="Validation F1-Score" strokeWidth={2.5} />
                <Line type="monotone" dataKey="far" stroke="#EF4444" name="False Alert Rate (FAR)" strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};
