"""Request models of the web API (validated by FastAPI/pydantic)."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Platform = Literal["Instagram", "TikTok", "YouTube", "Bilibili", "RedNote"]
MediaType = Literal["video", "image", "text", "mixed"]
Category = Literal["beauty", "lifestyle", "tech"]


class PostInput(BaseModel):
    """A planned post, described only with what is known before publishing."""
    platform: Platform = "TikTok"
    content_type: MediaType = "video"
    content_category: Category = "beauty"
    language: Literal["English", "Spanish", "Chinese", "Hindi", "Japanese"] = "Spanish"
    is_sponsored: bool = False
    sponsor_category: str = "Not sponsors"
    disclosure_type: Literal["explicit", "implicit", "none"] = "none"
    disclosure_location: Literal["caption", "video", "hashtags", "none"] = "none"
    weekday: Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] = "Friday"
    hour: int = Field(9, ge=0, le=23)
    follower_count: int = Field(25_000, ge=1, le=10_000_000)
    content_length: int = Field(45, ge=1, le=3_600)
    n_hashtags: int = Field(3, ge=0, le=30)
    caption_words: int = Field(15, ge=0, le=500)
    audience_gender_distribution: Literal["female", "male", "non-binary", "unknown"] = "female"
    audience_age_distribution: Literal["13-18", "19-25", "26-35", "36-50", "50+"] = "19-25"
    audience_location: Literal["USA", "China", "India", "Japan", "Brazil", "Germany", "UK", "Russia"] = "USA"
    creator_id: str | None = Field(None, description="opcional: usa o histórico deste creator")
    objetivo: Literal["qualquer", "views", "likes", "comments_count"] = Field("qualquer", description="métrica que a sugestão deve melhorar")

    @model_validator(mode="after")
    def organic_posts_have_no_sponsor(self):
        if not self.is_sponsored:
            self.sponsor_category, self.disclosure_type, self.disclosure_location = "Not sponsors", "none", "none"
        elif self.sponsor_category == "Not sponsors":
            self.sponsor_category = "electronics"
        return self


class ExploreQuery(BaseModel):
    """State of the dashboard slicers and visual settings."""
    filtros: dict[str, list[str]] = Field(default_factory=dict)
    dimensao: str = "platform"
    metrica: str = "views"
    linha: str = "platform"
    coluna: str = "content_type"
    de: str | None = None
    ate: str | None = None
    graficos: list[str] | None = None


class AudienceQuery(BaseModel):
    """Audience clustering: optional platform/format/theme filter and number of groups (None = automatic)."""
    platform: Platform | None = None
    content_type: MediaType | None = None
    content_category: Category | None = None
    k: int | None = Field(None, ge=2, le=6, description="nº de grupos; vazio = automático")
