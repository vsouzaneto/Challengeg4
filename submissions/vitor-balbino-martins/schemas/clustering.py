from pydantic import BaseModel, Field


class ClusteringRequest(BaseModel):
    dataset: str = "customer_support_tickets.csv"
    clusters: int = Field(default=12, ge=2, le=100)
    batch_size: int = Field(default=256, ge=32, le=2048)
    representatives: int = Field(default=5, ge=1, le=20)


class ClusteringResponse(BaseModel):
    dataset: str
    total_records: int
    clusters: int
    model: str
    groups: list[dict]
