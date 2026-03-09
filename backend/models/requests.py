from typing import Literal
from pydantic import BaseModel, Field, model_validator


class SearchParams(BaseModel):
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    method: Literal["template", "feature", "multi_scale"] = "multi_scale"
    scale_min: float = Field(default=0.5, ge=0.1, le=5.0)
    scale_max: float = Field(default=1.5, ge=0.1, le=5.0)

    @model_validator(mode="after")
    def _check_scale_range(self) -> "SearchParams":
        if self.scale_min >= self.scale_max:
            raise ValueError(
                f"scale_min ({self.scale_min}) must be less than scale_max ({self.scale_max})"
            )
        return self
