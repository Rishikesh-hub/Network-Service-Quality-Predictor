export interface PredictionRequest {
  packet_loss: number;
  jitter: number;
  rtt: number;
  outflow_Router: number;
  inflow_Router: number;
  resolve: number;
  ttl: number;
  probe_duration: number;
  link: string;
}

export interface Contributor {
  feature: string;
  raw_feature_name: string;
  value: number;
  importance_score: number;
  direction: 'risk_up' | 'risk_down' | 'neutral';
  method: string;
}

export interface PredictionResponse {
  prediction_id: number | null;
  probability: number;
  threshold: number;
  prediction: number;
  status: 'NORMAL' | 'DEGRADED';
  prediction_type: string;
  model_version: string;
  contributors: Contributor[];
  telemetry: PredictionRequest;
}

export interface ModelMetadata {
  model_version: string;
  model_type: string;
  architecture: number[];
  activation: string;
  solver: string;
  alpha: number;
  threshold: number;
  prediction_type: string;
  feature_count: number;
  validation_f1: number;
  validation_far: number;
  final_test_f1: number;
  final_test_far: number;
}

export interface TelemetryRecord {
  timestamp?: number;
  datetime?: string;
  link: string;
  packet_loss: number;
  jitter: number;
  rtt: number;
  outflow_Router: number;
  inflow_Router: number;
  resolve?: number;
  ttl?: number;
  probe_duration?: number;
  degradation?: number;
}

export interface TelemetryResponse {
  total: number;
  limit: number;
  offset: number;
  records: TelemetryRecord[];
  summary_stats: Record<string, { mean: number; median: number; min: number; max: number; std: number }>;
  links: string[];
}

export interface AlertItem {
  id: number;
  prediction_id?: number;
  timestamp: string;
  link: string;
  probability: number;
  threshold: number;
  status: 'ACTIVE' | 'RESOLVED';
  created_at: string;
}

export interface AlertsResponse {
  alerts: AlertItem[];
  active_count: number;
  recent_predictions: any[];
}

export interface MetricsResponse {
  official_threshold: number;
  prediction_type: string;
  validation: {
    threshold: number;
    f1: number;
    false_alert_rate: number;
    precision: number;
    recall: number;
  };
  test: {
    threshold: number;
    f1: number;
    false_alert_rate: number;
    precision: number;
    recall: number;
    default_threshold_050: {
      f1: number;
      false_alert_rate: number;
    };
  };
  benchmarks: Array<{
    model: string;
    precision: string;
    recall: string;
    f1: string;
    far: string;
    threshold: number;
  }>;
  threshold_curve: Array<{
    threshold: number;
    f1: number;
    far: number;
  }>;
}

export interface BoundaryTestResult {
  'Scenario ID': number;
  Scenario: string;
  'Input Summary': string;
  Probability: string;
  'Raw Probability': number;
  Prediction: 'NORMAL' | 'DEGRADED';
  Threshold: string;
  'Expected Behavior': string;
  Status: 'PASS' | 'REVIEW';
}
