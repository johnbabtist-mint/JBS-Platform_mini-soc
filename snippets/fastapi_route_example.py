"""
JBS Mini-SOC — FastAPI route example

This is a simplified public code sample based on the architecture style of the
private JBS Security Platform project. It shows the API shape and response
contract style without exposing production internals or private runtime data.
"""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class DashboardMetric(BaseModel):
    name: str
    value: int | float | str
    status: str


class DashboardMetricsResponse(BaseModel):
    source: str
    metrics: list[DashboardMetric]


@router.get("/api/dashboard/metrics", response_model=DashboardMetricsResponse)
def dashboard_metrics() -> DashboardMetricsResponse:
    """
    Return dashboard metrics in a stable contract.

    In the full private project, this endpoint is backed by deterministic
    runtime/repaired analytics services. This sample intentionally returns
    static example data.
    """
    return DashboardMetricsResponse(
        source="sample_public_contract",
        metrics=[
            DashboardMetric(name="risk_score", value=72, status="elevated"),
            DashboardMetric(name="active_sources", value=18, status="observed"),
            DashboardMetric(name="blocked_entities", value=5, status="protected"),
        ],
    )
