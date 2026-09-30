from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    dataset: str = "customer_support_tickets.csv"
    hourly_cost: float | None = Field(default=None, ge=0)


class StageUpdate(BaseModel):
    stage: str = Field(pattern="^(new|triage|progress|done)$")
