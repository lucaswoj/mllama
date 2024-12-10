from typing import Optional
from pydantic import BaseModel


class ChunkEvent(BaseModel):
    response: str


class EndEvent(BaseModel):
    done_reason: Optional[str] = None
    total_duration: int = 0
    load_duration: int = 0
    prompt_eval_count: int = 0
    prompt_eval_duration: int = 0
    eval_count: int = 0
    eval_duration: int = 0
