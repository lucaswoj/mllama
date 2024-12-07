from pydantic import BaseModel


class V1Function(BaseModel):
    name: str
    description: str = ""
    parameters: dict = {}
