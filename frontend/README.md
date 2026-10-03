# NSQP React.js Frontend
### Network Service Quality Predictor (NSQP) - TEAM-02
**NOC Operations Console (React.js + Vite + TypeScript + Saffron UI)**

---

## 🎨 Design System
Premium saffron-themed telecommunications Operations & Analytics Console:
* **Primary Saffron:** `#F59E0B`
* **Deep Saffron:** `#D97706`
* **Background:** `#0B0A08`
* **Panels:** `#15120D`
* **Elevated Panels:** `#1D1810`
* **Borders:** `#3A2A16`
* **Status Badges:** `✓ NORMAL` (`#22C55E`), `! DEGRADED` (`#EF4444`)

---

## 🚀 Quickstart

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
Open browser at: `http://localhost:5173`

To build for production:
```bash
npm run build
```

---

## 🧭 Routes & Pages

* `/dashboard` - Primary status banner, probability gauge (with 80% threshold marker), 5 KPI cards, contributing measurements, and historical trend charts.
* `/prediction` - Real-time QoS classification with 9 raw telemetry inputs and quick demo presets.
* `/telemetry` - Historical telemetry data explorer with link filters and summary statistics.
* `/alerts` - Persistent operational incident alerts ($P \ge 0.80$).
* `/model-performance` - Official evaluation benchmarks ($F_1 = 0.9648$, $\text{FAR} = 1.1805\%$), architecture specs, and threshold tuning trajectory.
* `/boundary-tests` - Interactive test runner for all 10 edge scenarios.

---

## ⚙️ Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000
```
Requests to `/api` are also automatically proxied to `http://localhost:8000` via Vite development proxy.
