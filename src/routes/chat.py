from typing import List, Literal, Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from type.StreamItem import StreamItem
from type.Tool import Tool
import outlines


router = APIRouter()


@router.post("/api/chat")
def chat(
    messages: str,  # List[Message] | str,
    model: str = "mlx-community/OpenELM-3B",
    format: Optional[Literal["json"]] = None,
    options: Optional[dict] = None,
    stream: Optional[bool] = False,
    keep_alive: Optional[str] = None,
    tools: Optional[List[Tool]] = None,
):
    if tools is not None:
        raise NotImplementedError()

    if options is not None:
        raise NotImplementedError()

    if keep_alive is not None:
        raise NotImplementedError()

    print("loading...")
    if model.startswith("mlx-community/"):
        model_obj = outlines.models.mlxlm(model)
    else:
        model_obj = outlines.models.transformers(model)

    if format == "json":
        generator = outlines.generate.json(
            model_obj,
            '{"type": "object", "additionalProperties": true}',
        )
    else:
        generator = outlines.generate.text(model_obj)

    # TODO apply chat template
    print("responding...")
    prompt = messages
    if stream:

        def streaming_response():
            for item in generator(prompt, max_tokens=50):
                yield StreamItem(content=item)

        return StreamingResponse(streaming_response())
    else:
        return generator(prompt, max_tokens=50)


if __name__ == "__main__":
    print(chat("What is your favorite color?", format="json"))
