from pydantic import BaseModel


class Area(BaseModel):
    name: str
    timing_project: str


areas = [Area(name="onNAV", timing_project="onNAV")]
