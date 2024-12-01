from typing import List, Literal, Optional
from fastapi.responses import StreamingResponse
from typing import List, Optional, Literal
from mlx_lm import load, stream_generate, generate
from fastapi import APIRouter
from type.Message import Message
from type.Tool import Tool

router = APIRouter()


@router.post("/api/chat")
async def chat(
    messages: List[Message] | str,
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
    messages = (
        messages
        if isinstance(messages, list)
        else [Message(role="user", content=messages)]
    )

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

    model_obj, tokenizer = load(model)

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    if stream:

        async def async_generator():
            for item in stream_generate(model_obj, tokenizer, prompt):
                yield item

        return StreamingResponse(async_generator())
    else:
        return generate(model_obj, tokenizer, prompt)
