from pydantic import BaseModel, HttpUrl, Field
from typing import Literal, Optional


class ExternalJobCreate(BaseModel):
    file_url: HttpUrl = Field(..., example="https://cdn.site.com/audio/abc.mp3")
    language: str = Field("fa")
    mode: Literal["transcribe_only", "transcribe_and_fix"] = "transcribe_only"
    callback_url: Optional[HttpUrl] = None


class JobQueuedResp(BaseModel):
    job_id: str
    status: Literal["queued"]
    estimated_cost: float


class JobStatusResp(BaseModel):
    job_id: str
    status: str
    mode: str
    raw_text: Optional[str]
    ai_text: Optional[str]
    charged: Optional[float]

    class Config:
        orm_mode = True
