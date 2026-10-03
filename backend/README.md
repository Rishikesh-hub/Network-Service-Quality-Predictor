# NSQP FastAPI Backend Service
### Network Service Quality Predictor (NSQP) - TEAM-02

FastAPI inference service wrapping the trained Artificial Neural Network (MLPClassifier 128x64) and preprocessing pipeline.

---

## 🚀 Quickstart

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger Documentation available at:
`http://localhost:8000/docs`

---

## 📡 API Endpoints

* `GET  /api/health` - Health status, loaded model architecture, operating threshold.
* `GET  /api/model` - Formal model specification and evaluation metrics.
* `POST /api/predict` - Real-time QoS classification with 26-feature contract enforcement.
* `GET  /api/telemetry` - Paginated historical telemetry inspection.
* `GET  /api/alerts` - Operational degradation alerts ($P \ge 0.80$).
* `GET  /api/metrics` - Official evaluated validation & test benchmarks.
* `GET  /api/boundary-tests` - Scenario definitions.
* `POST /api/boundary-tests/run` - Runs all 10 boundary scenarios.

---

## ⚙️ Environment Variables

```env
NSQP_MODEL_PATH=models/mlp_ann_final.pkl
NSQP_PREPROCESSOR_PATH=models/preprocessor.pkl
NSQP_RF_PATH=models/random_forest.pkl
NSQP_DB_PATH=data/nsqp_telemetry.db
NSQP_THRESHOLD=0.80
NSQP_DATA_PATH=data/network_qos_preprocessed/
```
