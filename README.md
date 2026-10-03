# JIG26_07 — Network Service Quality Predictor (NSQP)
### Track A: ANN & Predictive Analytics | TEAM-02
**Production Full-Stack Architecture: React.js (Vite + TS) + FastAPI + scikit-learn ANN**

---

## 📌 Executive Overview
**Network Service Quality Predictor (NSQP)** is an operational machine learning platform and telecommunications NOC console built to detect and classify current network Quality of Service (QoS) degradation on core campus network links.

* **Prediction Type:** **`CURRENT-STATE CLASSIFICATION`**
* **Future Prediction:** **`NOT SUPPORTED`** (advance-warning prediction could not be reliably constructed from the available multi-link bursty temporal resolution without target leakage).
* **Target Classes:** Binary classification:
  * `0 = NORMAL` (acceptable QoS, $P(\text{degraded}) < 0.80$)
  * `1 = DEGRADED` (degraded QoS, $P(\text{degraded}) \ge 0.80$)
* **Model Family:** Artificial Neural Network (`sklearn.neural_network.MLPClassifier`)
* **Architecture:** Hidden Layers `(128, 64)`, Activation `ReLU`, Optimizer `Adam`, Regularization $\alpha = 0.001$, Early Stopping enabled.
* **Exact Input Vector:** `26` contract-bound features (13 numeric with `num__` prefix + 13 one-hot categorical links with `cat__link_` prefix).
* **Operating Decision Threshold:** **`0.80`** (tuned on validation split F1-score to suppress false alert rates under bursty traffic).

---

## 📊 Validated Model Performance (Untouched Test Split)

| Metric | Validation Set (0.80) | Untouched Test Set (0.80) |
|---|---|---|
| **F1-Score** | **0.9511** | **0.9648** |
| **False Alert Rate (FAR)** | **1.0488%** | **1.1805%** |
| **Precision** | **93.14%** | **93.85%** |
| **Recall** | **97.16%** | **99.28%** |
| **Accuracy** | **98.24%** | **98.81%** |

$$\text{False Alert Rate (FAR)} = \frac{\text{FP}}{\text{FP} + \text{TN}} = \frac{262}{21,932 + 262} = 1.1805\%$$

---

## 📂 Project Directory Structure

```text
Network Service Quality Predictor/
│
├── data/
│   ├── network_qos_preprocessed/      # 180,011 cleaned labeled observations
│   │   ├── qos_labeled_cleaned.csv    # Primary dataset
│   │   ├── X_train_ann_logistic.csv
│   │   ├── X_validation_ann_logistic.csv
│   │   ├── X_test_ann_logistic.csv
│   │   ├── y_train_binary.csv
│   │   ├── y_validation_binary.csv
│   │   ├── y_test_binary.csv
│   │   ├── preprocessing_summary.json
│   │   └── wue/ntnu throughput files  # Supplementary throughput benchmarks
│   └── nsqp_telemetry.db              # SQLite persistence (Audit trail & alerts)
│
├── models/
│   ├── mlp_ann_final.pkl              # Final Tuned MLP/ANN Model Artifact (128, 64)
│   ├── preprocessor.pkl               # Fitted ColumnTransformer (Median Imputer + Scaler)
│   ├── random_forest.pkl              # Benchmark Model for Contributor Explanations
│   └── logistic_regression.pkl        # Baseline Comparison Model
│
├── backend/                           # FastAPI REST API Service (:8000)
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint with CORS & API routers
│   │   ├── config.py                  # Environment variables & path resolver
│   │   ├── api/                       # API Route Controllers
│   │   │   ├── health.py              # GET /api/health
│   │   │   ├── prediction.py          # POST /api/predict, GET /api/model
│   │   │   ├── telemetry.py           # GET /api/telemetry
│   │   │   ├── alerts.py              # GET /api/alerts
│   │   │   ├── metrics.py             # GET /api/metrics
│   │   │   └── boundary.py            # GET/POST /api/boundary-tests
│   │   ├── models/                    # Model Adapter
│   │   ├── features/                  # Feature Builder (26-feature contract)
│   │   ├── services/                  # Prediction, Telemetry, and Alert Services
│   │   ├── explanations/              # Random Forest importance weighting
│   │   └── repositories/              # SQLite persistence
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                          # React.js + Vite + TypeScript Saffron Console (:5173)
│   ├── src/
│   │   ├── api/client.ts              # Typed API Client
│   │   ├── components/Layout.tsx      # Saffron NOC Console Layout & Responsive Sidebar
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # Status banner, gauge, KPIs, trends, contributors
│   │   │   ├── Prediction.tsx         # Telemetry form, presets, real-time prediction
│   │   │   ├── Telemetry.tsx          # Historical telemetry explorer & stats
│   │   │   ├── Alerts.tsx             # Active alerts & SQLite prediction audit log
│   │   │   ├── ModelPerformance.tsx   # Evaluated metrics matrix & threshold curves
│   │   │   └── BoundaryTests.tsx      # 10 realistic edge scenarios runner
│   │   ├── types/index.ts             # TypeScript interfaces
│   │   ├── App.tsx                    # React Router routes
│   │   └── index.css                  # Saffron design system tokens
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
├── configs/                           # Model & 26-Feature configuration specifications
├── tests/                             # Automated test suite (21 unit & API tests passed)
├── dashboard.py                       # Standalone Streamlit console (alternative MVP)
├── final_model_report.md              # 18-Section Formal Engineering Report
└── README.md                          # Master documentation
```

---

## 🚀 Execution Instructions

### 1. Launch FastAPI Backend Service (Port 8000)
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Swagger Interactive Docs:** `http://127.0.0.1:8000/docs`
* **Healthcheck:** `http://127.0.0.1:8000/api/health`

### 2. Launch React.js Frontend (Port 5173)
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
* **NOC Web Console:** `http://127.0.0.1:5173`

### 3. Run Automated Test Suite (21 Tests)
```bash
python -m pytest tests -v
```

---

## 📡 Backend API Endpoints

| HTTP Method | Route | Description |
|---|---|---|
| `GET` | `/api/health` | Model status, architecture, threshold, and feature count. |
| `GET` | `/api/model` | Model specifications and official evaluation metrics. |
| `POST` | `/api/predict` | Predicts QoS state from 9 raw inputs (26-feature contract). |
| `GET` | `/api/telemetry` | Paginated historical telemetry records and summary statistics. |
| `GET` | `/api/alerts` | Active incident alerts ($P \ge 0.80$) and prediction audit trail. |
| `GET` | `/api/metrics` | Official validation and test evaluation benchmarks. |
| `GET` | `/api/boundary-tests` | Predefined boundary scenario metadata. |
| `POST` | `/api/boundary-tests/run` | Executes all 10 boundary scenarios through the model. |

---

## ⚙️ Environment Variables

### Backend
```env
NSQP_MODEL_PATH=models/mlp_ann_final.pkl
NSQP_PREPROCESSOR_PATH=models/preprocessor.pkl
NSQP_RF_PATH=models/random_forest.pkl
NSQP_DB_PATH=data/nsqp_telemetry.db
NSQP_THRESHOLD=0.80
NSQP_DATA_PATH=data/network_qos_preprocessed/
```

### Frontend
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🧪 Boundary Testing Execution Matrix

| ID | Scenario | Input Summary | P(Degraded) | Prediction | Threshold | Expected | Status |
|---|---|---|---|---|---|---|---|
| 1 | Normal network | Loss=0.0%, RTT=1.2ms, Jitter=0.12ms | 0.00% | NORMAL | 0.80 | NORMAL | **PASS** |
| 2 | High packet loss | Loss=5.0%, RTT=1.2ms, Jitter=0.12ms | 100.00% | DEGRADED | 0.80 | DEGRADED | **PASS** |
| 3 | High RTT | Loss=0.0%, RTT=35.0ms, Jitter=0.12ms | 100.00% | DEGRADED | 0.80 | DEGRADED | **PASS** |
| 4 | High jitter | Loss=0.0%, RTT=1.2ms, Jitter=3.5ms | 0.00% | NORMAL | 0.80 | DEGRADED | **REVIEW** |
| 5 | High packet loss + high RTT | Loss=4.0%, RTT=25.0ms, Jitter=0.12ms | 100.00% | DEGRADED | 0.80 | DEGRADED | **PASS** |
| 6 | High jitter + high RTT | Loss=0.0%, RTT=25.0ms, Jitter=3.0ms | 99.16% | DEGRADED | 0.80 | DEGRADED | **PASS** |
| 7 | Multiple indicators | Loss=6.0%, RTT=40.0ms, Jitter=3.5ms | 100.00% | DEGRADED | 0.80 | DEGRADED | **PASS** |
| 8 | Low traffic / idle | Loss=0.0%, RTT=0.8ms, Outflow=0.1 | 0.00% | NORMAL | 0.80 | NORMAL | **PASS** |
| 9 | Near training boundary | Loss=0.35%, RTT=12.0ms, Jitter=1.0ms | 98.74% | DEGRADED | 0.80 | DEGRADED | **PASS** |
| 10 | Missing telemetry | Missing packet_loss, jitter & probe | 0.00% | NORMAL | 0.80 | NORMAL | **PASS** |

* **Model Integrity:** Scenario 4 returns `REVIEW` honestly, exposing that isolated jitter spikes without concurrent latency or packet loss do not cross the 0.80 threshold.

---

## 🎯 Final Acceptance Verification

```text
==================================================
NSQP FINAL VERIFICATION
==================================================

DATASET DISCOVERY: PASS
MODEL ARTIFACTS: PASS
PREPROCESSOR: PASS
FEATURE CONTRACT: PASS
THRESHOLD: PASS

BACKEND HEALTH: PASS
MODEL API: PASS
PREDICTION API: PASS
SQLITE: PASS

PYTHON TESTS: PASS
FRONTEND BUILD: PASS
REACT -> FASTAPI: PASS

DASHBOARD: PASS
TELEMETRY: PASS
PREDICTION: PASS
ALERTS: PASS
MODEL PERFORMANCE: PASS
BOUNDARY TESTS: PASS

RESPONSIVE UI: PASS

FUTURE PREDICTION:
NOT SUPPORTED

PREDICTION TYPE:
CURRENT-STATE CLASSIFICATION

OFFICIAL THRESHOLD:
0.80

TEST F1:
0.9648

TEST FAR:
1.1805%

==================================================
```
