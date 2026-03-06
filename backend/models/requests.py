from typing import Literal
from pydantic import BaseModel, Field


class SearchParams(BaseModel):
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    method: Literal["template", "feature", "multi_scale"] = "multi_scale"
    scale_min: float = Field(default=0.5, ge=0.1, le=1.0)
    scale_max: float = Field(default=1.5, ge=1.0, le=5.0)
