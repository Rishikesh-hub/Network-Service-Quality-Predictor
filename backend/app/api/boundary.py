"""
Boundary test endpoints.
"""

from fastapi import APIRouter, HTTPException
from src.evaluation.boundary_testing import BoundaryTester

router = APIRouter()
boundary_tester = BoundaryTester()


@router.get("/boundary-tests")
def get_boundary_scenarios():
    try:
        scenarios = boundary_tester.get_scenarios()
        # Return summary without executing
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "summary": s["summary"],
                "expected": s["expected"],
                "raw_input": s["raw_input"]
            }
            for s in scenarios
        ]
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/boundary-tests/run")
def run_boundary_tests():
    try:
        df_res = boundary_tester.run_all_tests(threshold=0.80)
        return df_res.to_dict(orient="records")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
