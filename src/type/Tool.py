from pydantic import BaseModel


class Tool(BaseModel):
    name: str
    inputs: dict
    outputs: dict
