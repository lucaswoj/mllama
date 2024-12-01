from typing import List, Literal, Optional
from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from type.Message import Message
from type.Tool import Tool
from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
from langchain_core.messages import HumanMessage

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

    lc_llm = MLXPipeline.from_model_id(
        model,
        pipeline_kwargs={"max_tokens": 10, "temp": 0.1},
    )
    lc_model = ChatMLX(llm=lc_llm)

    lc_messages = (
        [HumanMessage(content=message.content) for message in messages]
        if isinstance(messages, list)
        else [HumanMessage(content=messages)]
    )

    if stream:
        raise NotImplementedError()
    else:
        response = lc_model.invoke(lc_messages)
        return response.content
