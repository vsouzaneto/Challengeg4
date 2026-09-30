from pydantic import BaseModel, Field

class RagQuery(BaseModel):
    query: str = Field(min_length=2)
    k: int = Field(default=5, ge=1, le=50)

class RagIndexResponse(BaseModel):
    status: str
    message: str

class RagSearchResult(BaseModel):
    content: str
    metadata: dict
    score: float | None = None
