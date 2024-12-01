from typing import List, Literal, Optional
from fastapi import APIRouter
from type.Message import Message
from type.Tool import Tool
from outlines import generate, models


router = APIRouter()

schema = """{
    "title": "Character",
    "type": "object",
    "properties": {
        "name": {
            "title": "Name",
            "maxLength": 10,
            "type": "string"
        },
        "age": {
            "title": "Age",
            "type": "integer"
        },
        "armor": {"$ref": "#/definitions/Armor"},
        "weapon": {"$ref": "#/definitions/Weapon"},
        "strength": {
            "title": "Strength",
            "type": "integer"
        }
    },
    "required": ["name", "age", "armor", "weapon", "strength"],
    "definitions": {
        "Armor": {
            "title": "Armor",
            "description": "An enumeration.",
            "enum": ["leather", "chainmail", "plate"],
            "type": "string"
        },
        "Weapon": {
            "title": "Weapon",
            "description": "An enumeration.",
            "enum": ["sword", "axe", "mace", "spear", "bow", "crossbow"],
            "type": "string"
        }
    }
}"""


@router.post("/api/chat")
def chat(
    messages: str,  # List[Message] | str,
    model: str = "mlx-community/Llama-3.2-3B-Instruct",
    format: Optional[Literal["json"]] = None,
    options: Optional[dict] = None,
    stream: Optional[bool] = False,
    keep_alive: Optional[str] = None,
    tools: Optional[List[Tool]] = None,
):
    """
    Generate the next message in a chat with a provided model.
    """
    if not model.startswith("mlx-community/"):
        raise ValueError("Model name must start with 'mlx-community/'")

    if tools is not None:
        raise NotImplementedError()

    if format is not None:
        raise NotImplementedError()

    if options is not None:
        raise NotImplementedError()

    if keep_alive is not None:
        raise NotImplementedError()

    if stream:
        raise NotImplementedError()

    model_obj = models.mlxlm(model)
    generator = generate.json(model_obj, schema)
    return generator(messages)


if __name__ == "__main__":
    print(chat("Hello, how are you?"))
