"""
Prediction and Model metadata endpoints.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from backend.app.services.prediction_service import BackendPredictionService

router = APIRouter()
prediction_service = BackendPredictionService()


class PredictionRequest(BaseModel):
    packet_loss: float = Field(..., description="Packet loss percentage (0.0 to 100.0)")
    jitter: float = Field(..., description="Packet arrival jitter in milliseconds")
    rtt: float = Field(..., description="Round-trip time in milliseconds")
    outflow_Router: float = Field(..., description="Outflow router throughput in Mbps")
    inflow_Router: float = Field(..., description="Inflow router throughput in Mbps")
    resolve: float = Field(..., description="DNS resolve time in seconds")
    ttl: float = Field(..., description="Time To Live hop metric")
    probe_duration: float = Field(..., description="Active probe execution duration in seconds")
    link: str = Field(..., description="Core network link identifier (e.g. 'R1-R2')")


@router.post("/predict")
def predict_qos(payload: PredictionRequest):
    try:
        data_dict = payload.model_dump()
        result = prediction_service.predict_single(data_dict)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(ex)}"
        )


@router.get("/model")
def get_model_metadata():
    try:
        return prediction_service.get_metadata()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))
