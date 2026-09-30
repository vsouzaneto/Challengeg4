from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    dataset: str = "customer_support_tickets.csv"
    chunk_size: int = Field(default=100, ge=10, le=500)
    hourly_cost: float | None = Field(default=None, ge=0)


class ReportResponse(BaseModel):
    dataset: str
    metrics: dict
    extraction: dict
    consolidation: dict
    audit: dict
