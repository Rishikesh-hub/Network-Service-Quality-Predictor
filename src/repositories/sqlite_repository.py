"""
SQLite Repository for Network Service Quality Predictor
Implements Document 05 schema: telemetry, predictions, alerts, boundary tests.
"""

from typing import Dict, Any, List, Optional
import os
import sqlite3
import json
from datetime import datetime, timezone


DB_PATH_DEFAULT = os.path.join("data", "nsqp_telemetry.db")


class SQLiteRepository:
    """Manages persistence for predictions, audit trail, alerts, and boundary test runs."""

    def __init__(self, db_path: str = DB_PATH_DEFAULT):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes schema tables according to Document 05."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                link TEXT NOT NULL,
                probability REAL NOT NULL,
                threshold REAL NOT NULL,
                prediction INTEGER NOT NULL,
                status TEXT NOT NULL,
                prediction_type TEXT NOT NULL DEFAULT 'current_state',
                model_version TEXT NOT NULL,
                raw_payload TEXT,
                feature_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                link TEXT NOT NULL,
                probability REAL NOT NULL,
                threshold REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS boundary_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_name TEXT NOT NULL,
                input_summary TEXT NOT NULL,
                probability REAL,
                threshold REAL NOT NULL,
                prediction INTEGER,
                expected_behavior TEXT NOT NULL,
                status TEXT NOT NULL,
                model_version TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()

    def record_prediction(self, record: Dict[str, Any], probability: float, threshold: float,
                          prediction: int, status: str, link: str, features_dict: Dict[str, float],
                          model_version: str = "mlp_ann_final") -> int:
        """Saves a prediction audit record and triggers alert if degraded."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO predictions (timestamp, link, probability, threshold, prediction, status, prediction_type, model_version, raw_payload, feature_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'current_state', ?, ?, ?, ?)
            """, (
                now,
                link,
                float(probability),
                float(threshold),
                int(prediction),
                status,
                model_version,
                json.dumps(record),
                json.dumps(features_dict),
                now
            ))
            pred_id = cursor.lastrowid

            # Alert triggered if probability >= threshold
            if prediction == 1:
                # Deduplication check: check if an active alert already exists on this link
                cursor.execute("""
                SELECT id FROM alerts WHERE link = ? AND status = 'ACTIVE' LIMIT 1
                """, (link,))
                existing = cursor.fetchone()
                if not existing:
                    cursor.execute("""
                    INSERT INTO alerts (prediction_id, timestamp, link, probability, threshold, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
                    """, (pred_id, now, link, float(probability), float(threshold), now))

            conn.commit()
            return pred_id

    def get_recent_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent prediction records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Fetches active alerts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts WHERE status = 'ACTIVE' ORDER BY id DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def record_boundary_test(self, scenario: str, summary: str, prob: float, threshold: float,
                             pred: int, expected: str, status: str, model_version: str = "mlp_ann_final"):
        """Saves a boundary test result."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO boundary_tests (scenario_name, input_summary, probability, threshold, prediction, expected_behavior, status, model_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (scenario, summary, float(prob), float(threshold), int(pred), expected, status, model_version))
            conn.commit()
