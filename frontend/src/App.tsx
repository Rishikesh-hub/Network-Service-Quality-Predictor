import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Prediction } from './pages/Prediction';
import { Telemetry } from './pages/Telemetry';
import { Alerts } from './pages/Alerts';
import { ModelPerformance } from './pages/ModelPerformance';
import { BoundaryTests } from './pages/BoundaryTests';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="prediction" element={<Prediction />} />
          <Route path="telemetry" element={<Telemetry />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="model-performance" element={<ModelPerformance />} />
          <Route path="boundary-tests" element={<BoundaryTests />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
