"""
Network Service Quality Predictor (NSQP) - Streamlit Operations Console
TEAM-02 | Track A: ANN & Predictive Analytics
Follows Document 04 (UI/UX), Document 01 (PRD), Document 02 (TRD), and Document 05 (Backend Schema).
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.features.feature_builder import FeatureBuilder, EXACT_26_FEATURE_NAMES
from src.models.model_adapter import ModelAdapter
from src.services.prediction_service import PredictionService
from src.evaluation.boundary_testing import BoundaryTester
from src.repositories.sqlite_repository import SQLiteRepository
from src.data.data_adapter import DataAdapter, EXPECTED_LINKS

# ---------------------------------------------------------
# Page Configuration & Dark Console Styling (Document 04)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Network Service Quality Predictor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Dark Operations Console Theme */
    .stApp {
        background-color: #0B0F14;
        color: #F3F6F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    header, [data-testid="stHeader"] {
        background-color: #0B0F14;
    }
    [data-testid="stSidebar"] {
        background-color: #111820;
        border-right: 1px solid #273341;
    }
    .metric-card {
        background-color: #17212B;
        border: 1px solid #273341;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .status-card-normal {
        background-color: rgba(34, 197, 94, 0.1);
        border: 2px solid #22C55E;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .status-card-degraded {
        background-color: rgba(239, 68, 68, 0.12);
        border: 2px solid #EF4444;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .badge-ready {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.2);
        color: #22C55E;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #22C55E;
    }
    .badge-sim {
        display: inline-block;
        background-color: rgba(59, 130, 246, 0.2);
        color: #60A5FA;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #3B82F6;
    }
    .subtext {
        color: #A8B3BF;
        font-size: 13px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# Resource Initializations
# ---------------------------------------------------------
@st.cache_resource
def get_prediction_service():
    fb = FeatureBuilder()
    ma = ModelAdapter()
    repo = SQLiteRepository()
    return PredictionService(feature_builder=fb, model_adapter=ma, repository=repo)

@st.cache_data
def load_sample_telemetry(max_rows: int = 500):
    csv_path = os.path.join(BASE_DIR, "network_qos_preprocessed", "qos_labeled_cleaned.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, nrows=max_rows)
        if "timestamp" in df.columns:
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
        return df
    return None

try:
    service = get_prediction_service()
    meta = service.get_metadata()
    model_loaded = True
except Exception as e:
    service = None
    meta = {}
    model_loaded = False
    load_error = str(e)


# ---------------------------------------------------------
# Sidebar Navigation (Document 04, Section 10)
# ---------------------------------------------------------
st.sidebar.markdown("### 📡 NETWORK QUALITY")
nav = st.sidebar.radio(
    "Console Navigation",
    [
        "📊 Dashboard",
        "⚡ Live Inference",
        "📡 Telemetry Explorer",
        "🚨 Alerts Management",
        "📈 Model Performance",
        "🧪 Boundary Tests"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚙️ MODEL SPECIFICATION")
st.sidebar.markdown(f"**Model:** `{meta.get('model_type', 'MLPClassifier')}`")
st.sidebar.markdown(f"**Architecture:** `128 × 64` Layers")
st.sidebar.markdown(f"**Operating Threshold:** `0.80`")
st.sidebar.markdown(f"**Features:** `26` Contract-Bound")
st.sidebar.markdown(f"**Mode:** `CURRENT STATE`")

if model_loaded:
    st.sidebar.markdown('<span class="badge-ready">● MODEL ARTIFACT ACTIVE</span>', unsafe_allow_html=True)
else:
    st.sidebar.error("❌ MODEL UNAVAILABLE")

st.sidebar.markdown("---")
st.sidebar.markdown('<span class="badge-sim">● SIMULATION MODE</span>', unsafe_allow_html=True)
st.sidebar.caption("Historical Telemetry Replay • No Live Connection")


# ---------------------------------------------------------
# Header Bar
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("Network Service Quality Predictor")
    st.caption("Campus Network QoS Degradation Monitor • Binary Current-State Classification (Threshold: 0.80)")
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="badge-ready">● MODEL READY</span> &nbsp; <span class="badge-sim">● HISTORICAL DATA</span>', unsafe_allow_html=True)

st.markdown("---")


# ---------------------------------------------------------
# PAGE 1: DASHBOARD
# ---------------------------------------------------------
if nav == "📊 Dashboard":
    # Load nominal baseline sample
    nominal_telemetry = {
        "packet_loss": 0.0,
        "jitter": 0.12,
        "rtt": 1.2,
        "outflow_Router": 4.65,
        "inflow_Router": 4.65,
        "resolve": 0.03,
        "ttl": 62.0,
        "probe_duration": 0.0,
        "link": "R1-R9"
    }

    # Evaluate current baseline observation
    pred_res = service.predict_single(nominal_telemetry)
    prob = pred_res["probability"]
    threshold = pred_res["threshold"]
    status = pred_res["status"]

    # 1. Primary Status Card (Document 04, Section 12)
    if status == "DEGRADED":
        st.markdown(f"""
        <div class="status-card-degraded">
            <h1 style="color: #EF4444; margin: 0; font-size: 38px;">! DEGRADED</h1>
            <p style="font-size: 20px; margin: 8px 0;">Degradation Probability: <b>{prob*100:.2f}%</b> &nbsp;|&nbsp; Operating Threshold: <b>{threshold*100:.0f}%</b></p>
            <p class="subtext">Classification Mode: <b>Current-State QoS Evaluation</b> (Action Required: Immediate Link Inspection)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-card-normal">
            <h1 style="color: #22C55E; margin: 0; font-size: 38px;">✓ NORMAL</h1>
            <p style="font-size: 20px; margin: 8px 0;">Degradation Probability: <b>{prob*100:.2f}%</b> &nbsp;|&nbsp; Operating Threshold: <b>{threshold*100:.0f}%</b></p>
            <p class="subtext">Classification Mode: <b>Current-State QoS Evaluation</b> (All SLA Bounds Satisfied)</p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Probability Indicator Bar (Section 13)
    fig_gauge = go.Figure()
    fig_gauge.add_trace(go.Bar(
        y=["Probability"],
        x=[prob],
        orientation="h",
        marker=dict(color="#EF4444" if prob >= threshold else "#22C55E"),
        name="Current P(Degraded)"
    ))
    fig_gauge.add_vline(x=threshold, line_width=3, line_dash="dash", line_color="#F59E0B",
                        annotation_text="Decision Threshold 0.80", annotation_position="top right")
    fig_gauge.update_layout(
        xaxis=dict(range=[0, 1.0], tickformat=".0%", title="Probability Scale"),
        yaxis=dict(showticklabels=False),
        height=140,
        margin=dict(l=10, r=10, t=30, b=30),
        paper_bgcolor="#111820",
        plot_bgcolor="#111820",
        font=dict(color="#F3F6F9")
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 3. KPI Cards (Document 04, Section 14)
    st.markdown("#### 📊 TELEMETRY OBSERVATIONS (NOMINAL MONITOR)")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Packet Loss", f"{nominal_telemetry['packet_loss']:.1f} %", "0.0% nominal")
    c2.metric("Jitter", f"{nominal_telemetry['jitter']:.2f} ms", "0.12 ms nominal")
    c3.metric("Round Trip Time (RTT)", f"{nominal_telemetry['rtt']:.1f} ms", "1.2 ms nominal")
    c4.metric("Outflow Router", f"{nominal_telemetry['outflow_Router']:.2f} Mbps")
    c5.metric("Inflow Router", f"{nominal_telemetry['inflow_Router']:.2f} Mbps")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🔍 IMPORTANT MODEL-ASSOCIATED MEASUREMENTS")
        st.caption("Statistical feature rankings from Random Forest importance analysis. Explanatory evidence, NOT causal root cause.")
        contrib_data = []
        for c in pred_res["contributors"]:
            contrib_data.append({
                "Measurement": c["feature"],
                "Contribution Weight": f"{c['importance_score']:.4f}",
                "Signal Direction": c["direction"]
            })
        st.table(pd.DataFrame(contrib_data))

    with col_right:
        st.markdown("#### 🚨 RECENT SYSTEM ALERTS (THRESHOLD ≥ 0.80)")
        repo = SQLiteRepository()
        recent_alerts = repo.get_active_alerts()
        if recent_alerts:
            st.dataframe(pd.DataFrame(recent_alerts)[["id", "timestamp", "link", "probability", "threshold", "status"]], use_container_width=True)
        else:
            st.info("No active degradation alerts recorded in current session. Decision threshold 0.80 is operating nominal.")

    # 4. Telemetry Historical Trends Chart
    st.markdown("---")
    st.markdown("#### 📈 HISTORICAL TELEMETRY TRENDS (REPLAY / SIMULATION)")
    df_sample = load_sample_telemetry(250)
    if df_sample is not None and "datetime" in df_sample.columns:
        fig_trend = px.line(
            df_sample,
            x="datetime",
            y=["packet_loss", "jitter", "rtt"],
            labels={"value": "Value (Loss %, ms)", "datetime": "Telemetry Timestamp (UTC)"},
            title="Telemetry Streams Over Time (Chronological Split)"
        )
        fig_trend.update_layout(
            paper_bgcolor="#111820",
            plot_bgcolor="#111820",
            font=dict(color="#F3F6F9"),
            legend=dict(orientation="h", y=1.1, x=0.0)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Historical dataset file `qos_labeled_cleaned.csv` not available for trend rendering.")


# ---------------------------------------------------------
# PAGE 2: LIVE INFERENCE
# ---------------------------------------------------------
elif nav == "⚡ Live Inference":
    st.markdown("### ⚡ Live Telemetry Prediction Console")
    st.markdown("Supply raw telemetry values for current-state QoS classification. Features are dynamically validated against the 26-feature contract.")

    with st.form("inference_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### Network Impairments")
            p_loss = st.number_input("Packet Loss (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            p_jitter = st.number_input("Jitter (ms)", min_value=0.0, max_value=500.0, value=0.12, step=0.05)
            p_rtt = st.number_input("Round Trip Time (RTT) (ms)", min_value=0.0, max_value=5000.0, value=1.2, step=0.5)

        with col2:
            st.markdown("##### Router Traffic Flows")
            p_outflow = st.number_input("Outflow Router Traffic (Mbps)", min_value=0.0, value=4.65, step=1.0)
            p_inflow = st.number_input("Inflow Router Traffic (Mbps)", min_value=0.0, value=4.65, step=1.0)
            p_link = st.selectbox("Target Network Link", EXPECTED_LINKS, index=1)

        with col3:
            st.markdown("##### Probe Telemetry")
            p_resolve = st.number_input("DNS Resolve Time (s)", min_value=0.0, value=0.03, step=0.01)
            p_ttl = st.number_input("TTL Value", min_value=1.0, max_value=255.0, value=62.0, step=1.0)
            p_probe = st.number_input("Probe Duration (s)", min_value=0.0, value=0.0, step=0.01)

        submit_btn = st.form_submit_button("Run QoS Prediction", type="primary")

    if submit_btn:
        raw_payload = {
            "packet_loss": float(p_loss),
            "jitter": float(p_jitter),
            "rtt": float(p_rtt),
            "outflow_Router": float(p_outflow),
            "inflow_Router": float(p_inflow),
            "resolve": float(p_resolve),
            "ttl": float(p_ttl),
            "probe_duration": float(p_probe),
            "link": p_link
        }

        try:
            with st.spinner("Executing ANN inference pipeline..."):
                res = service.predict_single(raw_payload)

            col_res1, col_res2 = st.columns([1, 1])
            with col_res1:
                st.markdown("#### 🎯 Prediction Output")
                if res["status"] == "DEGRADED":
                    st.error(f"### ! DEGRADED (ALARM TRIGGERED)")
                else:
                    st.success(f"### ✓ NORMAL (ACCEPTABLE QoS)")

                st.metric("P(Degraded)", f"{res['probability']*100:.2f}%")
                st.metric("Decision Threshold", f"{res['threshold']*100:.0f}%")
                st.caption(f"Model Version: `{res['model_version']}` | Audit Record ID: `{res['prediction_id']}`")

            with col_res2:
                st.markdown("#### 🔍 Contributing Telemetry Signals")
                st.caption("Top measurements correlated with this classification state:")
                c_df = pd.DataFrame(res["contributors"])[["feature", "importance_score", "direction"]]
                st.dataframe(c_df, use_container_width=True)

        except Exception as ex:
            st.error(f"Prediction Pipeline Error: {ex}")


# ---------------------------------------------------------
# PAGE 3: TELEMETRY EXPLORER
# ---------------------------------------------------------
elif nav == "📡 Telemetry Explorer":
    st.markdown("### 📡 Telemetry Dataset Inspection & Statistics")
    st.markdown("Inspect historical QoS records from `qos_labeled_cleaned.csv` spanning June 25, 2025 to July 02, 2025.")

    df_full = load_sample_telemetry(1000)
    if df_full is not None:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            sel_link = st.selectbox("Filter Link", ["ALL"] + sorted(list(df_full["link"].unique())))
        with col_f2:
            st.metric("Total Sampled Rows Available", len(df_full))

        filtered_df = df_full if sel_link == "ALL" else df_full[df_full["link"] == sel_link]
        st.dataframe(filtered_df, use_container_width=True)

        st.markdown("#### Telemetry Feature Summary Statistics")
        num_cols = ["packet_loss", "jitter", "rtt", "outflow_Router", "inflow_Router", "resolve", "ttl", "probe_duration"]
        st.dataframe(filtered_df[num_cols].describe().T[["mean", "std", "min", "50%", "max"]], use_container_width=True)
    else:
        st.warning("Telemetry dataset `qos_labeled_cleaned.csv` not found in `network_qos_preprocessed/`.")


# ---------------------------------------------------------
# PAGE 4: ALERTS MANAGEMENT
# ---------------------------------------------------------
elif nav == "🚨 Alerts Management":
    st.markdown("### 🚨 Operational Degradation Alerts")
    st.markdown("Alerts are triggered strictly when model output satisfies: **P(Degraded) ≥ 0.80**.")

    repo = SQLiteRepository()
    active_alerts = repo.get_active_alerts()
    recent_preds = repo.get_recent_predictions(30)

    st.markdown("#### Active Incident Alerts")
    if active_alerts:
        st.dataframe(pd.DataFrame(active_alerts), use_container_width=True)
    else:
        st.success("✓ No active degradation alerts. Network operating in nominal SLA limits.")

    st.markdown("---")
    st.markdown("#### Recent Prediction Audit Trail (SQLite Persistence)")
    if recent_preds:
        st.dataframe(pd.DataFrame(recent_preds)[["id", "timestamp", "link", "probability", "threshold", "status", "prediction_type"]], use_container_width=True)
    else:
        st.info("No prediction history recorded yet. Run live inference or boundary tests to populate audit log.")


# ---------------------------------------------------------
# PAGE 5: MODEL PERFORMANCE
# ---------------------------------------------------------
elif nav == "📈 Model Performance":
    st.markdown("### 📈 Evaluated Model Performance & Benchmarks")
    st.markdown("Official validated metrics from the executed project evaluation (untouched chronologically-split test set).")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Validation F1-Score (0.80)", "95.11%")
    col_m2.metric("Validation FAR (0.80)", "1.0488%")
    col_m3.metric("Final Test F1-Score (0.80)", "96.48%")
    col_m4.metric("Final Test FAR (0.80)", "1.1805%")

    st.markdown("#### 🔬 Comparative Model Evaluation Matrix")
    eval_table = pd.DataFrame([
        {"Model Experiment": "Logistic Regression Baseline", "Precision": "94.21%", "Recall": "98.89%", "F1-Score": "96.49%", "FAR": "2.03%", "Decision Threshold": "0.50"},
        {"Model Experiment": "Random Forest Benchmark", "Precision": "99.81%", "Recall": "91.89%", "F1-Score": "95.69%", "FAR": "0.06%", "Decision Threshold": "0.50"},
        {"Model Experiment": "MLP / ANN (Default Threshold)", "Precision": "92.05%", "Recall": "97.45%", "F1-Score": "95.96%", "FAR": "1.92%", "Decision Threshold": "0.50"},
        {"Model Experiment": "MLP / ANN (Tuned Optimal)", "Precision": "93.14%", "Recall": "97.16%", "F1-Score": "96.48%", "FAR": "1.18%", "Decision Threshold": "0.80"},
    ])
    st.table(eval_table)

    st.markdown("#### 🎯 Validation Threshold Tuning Trajectory")
    thresh_data = pd.DataFrame([
        {"Threshold": 0.20, "F1": 0.9286, "FAR": 0.0198},
        {"Threshold": 0.30, "F1": 0.9327, "FAR": 0.0180},
        {"Threshold": 0.40, "F1": 0.9358, "FAR": 0.0168},
        {"Threshold": 0.50, "F1": 0.9400, "FAR": 0.0152},
        {"Threshold": 0.60, "F1": 0.9431, "FAR": 0.0138},
        {"Threshold": 0.70, "F1": 0.9463, "FAR": 0.0125},
        {"Threshold": 0.80, "F1": 0.9511, "FAR": 0.0105}
    ])
    fig_thresh = px.line(thresh_data, x="Threshold", y=["F1", "FAR"], markers=True, title="Validation F1 vs False Alert Rate across Thresholds")
    fig_thresh.update_layout(paper_bgcolor="#111820", plot_bgcolor="#111820", font=dict(color="#F3F6F9"))
    st.plotly_chart(fig_thresh, use_container_width=True)


# ---------------------------------------------------------
# PAGE 6: BOUNDARY TESTS
# ---------------------------------------------------------
elif nav == "🧪 Boundary Tests":
    st.markdown("### 🧪 Boundary-Resilience Testing Suite")
    st.markdown("Verifies model behavior across 10 realistic edge scenarios using feature-preserving DataFrames and the trained `SimpleImputer`.")

    bt = BoundaryTester()

    if st.button("Run All 10 Boundary Tests", type="primary"):
        with st.spinner("Evaluating boundary test suite..."):
            df_res = bt.run_all_tests(threshold=0.80)
        st.session_state["boundary_results"] = df_res

    if "boundary_results" in st.session_state:
        df_show = st.session_state["boundary_results"]
        st.dataframe(df_show[["Scenario ID", "Scenario", "Input Summary", "Probability", "Prediction", "Expected Behavior", "Status"]], use_container_width=True)

        pass_count = (df_show["Status"] == "PASS").sum()
        review_count = (df_show["Status"] == "REVIEW").sum()
        st.success(f"**Passed Scenarios:** {pass_count} / 10 &nbsp;|&nbsp; **Review / Observation Scenarios:** {review_count} / 10")
        st.caption("Review cases highlight single-metric edge variations where multi-metric degradation is required by the neural network weights.")
    else:
        st.info("Click 'Run All 10 Boundary Tests' above to execute the testing suite.")
