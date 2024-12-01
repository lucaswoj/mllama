from pydantic import BaseModel


class ToolCall(BaseModel):
    name: str
    inputs: dict
    outputs: dict
