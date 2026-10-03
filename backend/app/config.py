"""
Configuration module for NSQP FastAPI Backend.
Handles environment variables and dynamic path resolution.
"""

import os
from pathlib import Path

# Base project root resolution
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def resolve_path(env_var: str, default_rel: str) -> str:
    val = os.getenv(env_var)
    if val:
        p = Path(val)
        if p.is_absolute():
            return str(p)
        return str(BASE_DIR / p)
    return str(BASE_DIR / default_rel)


class Settings:
    PROJECT_NAME: str = "Network Service Quality Predictor API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    MODEL_PATH: str = resolve_path("NSQP_MODEL_PATH", "models/mlp_ann_final.pkl")
    PREPROCESSOR_PATH: str = resolve_path("NSQP_PREPROCESSOR_PATH", "models/preprocessor.pkl")
    RF_PATH: str = resolve_path("NSQP_RF_PATH", "models/random_forest.pkl")
    DB_PATH: str = resolve_path("NSQP_DB_PATH", "data/nsqp_telemetry.db")
    THRESHOLD: float = float(os.getenv("NSQP_THRESHOLD", "0.80"))
    DATA_PATH: str = resolve_path("NSQP_DATA_PATH", "data/network_qos_preprocessed")

    PRIMARY_DATASET_CSV: str = str(Path(DATA_PATH) / "qos_labeled_cleaned.csv")

    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]


settings = Settings()
