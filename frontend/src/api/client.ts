import {
  PredictionRequest,
  PredictionResponse,
  ModelMetadata,
  TelemetryResponse,
  AlertsResponse,
  MetricsResponse,
  BoundaryTestResult
} from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {})
      }
    });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  getHealth: () => request<{ status: string; model_loaded: boolean; model_version: string; threshold: number }>('/api/health'),
  getModelMetadata: () => request<ModelMetadata>('/api/model'),
  predictQoS: (payload: PredictionRequest) =>
    request<PredictionResponse>('/api/predict', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  getTelemetry: (link?: string, limit: number = 100, offset: number = 0) => {
    const params = new URLSearchParams();
    if (link && link !== 'ALL') params.append('link', link);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    return request<TelemetryResponse>(`/api/telemetry?${params.toString()}`);
  },
  getAlerts: (status?: string, limit: number = 50) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit.toString());
    return request<AlertsResponse>(`/api/alerts?${params.toString()}`);
  },
  getMetrics: () => request<MetricsResponse>('/api/metrics'),
  getBoundaryScenarios: () => request<any[]>('/api/boundary-tests'),
  runBoundaryTests: () =>
    request<BoundaryTestResult[]>('/api/boundary-tests/run', {
      method: 'POST'
    })
};
