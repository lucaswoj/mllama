from datetime import datetime
import json
import os
from time import time_ns
from fastapi import APIRouter, HTTPException
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, List, Dict, Any
import pal
import pal.events
from pal.model import Model
import pal.tools


class ToolFunction(BaseModel):
    name: str
    description: Optional[str]
    parameters: Any


class Tool(BaseModel):
    type: Literal["function"]
    function: ToolFunction


class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str]
    images: List[str] = []
    tool_calls: List[Tool] = []


class Params(BaseModel):
    model: Annotated[str, Field(description="the model name")]
    format: Annotated[
        Optional[Literal["json"] | Dict[str, Any]],
        Field(
            description="the format to return a response in. Format can be json or a JSON schema"
        ),
    ] = None
    options: Annotated[
        Dict[str, Any],
        Field(
            description="additional model parameters listed in the documentation for the Modelfile such as temperature"
        ),
    ] = {}
    stream: Annotated[
        bool,
        Field(
            description="if false the response will be returned as a single response object, rather than a stream of objects"
        ),
    ] = True
    keep_alive: Annotated[
        str,
        Field(
            description="controls how long the model will stay loaded into memory following the request (default: 5m)"
        ),
    ] = "5m"
    messages: List[Message]
    tools: List[Tool] = []


router = APIRouter()


@router.post("/api/chat")
async def chat(params: Params, request: fastapi.Request):

    if params.tools:
        raise HTTPException(status_code=501, detail="'tools' not implemented")

    last_message = (
        params.messages[-1].content.strip() if params.messages[-1].content else ""
    )

    start_time = time_ns()

    if os.environ["PAL_TOOLS"] is not None and last_message.startswith("/"):
        generator = pal.tools.generate(last_message, request.is_disconnected)
    else:
        model = Model.load(params.model, params.keep_alive)
        generator = model.generate(
            start_time=start_time,
            prompt=model.template(conversation=params.messages),
            options=params.options,
            format=params.format,
        )

    def format_end_event(event, response):
        return {
            "model": params.model,
            "message": {
                "role": "assistant",
                "content": response,
            },
            "created_at": datetime.now().isoformat(),
            "done_reason": event.done_reason,
            "done": True,
            "total_duration": event.total_duration,
            "load_duration": event.load_duration,
            "prompt_eval_count": event.prompt_eval_count,
            "prompt_eval_duration": event.prompt_eval_duration,
            "eval_count": event.eval_count,
            "eval_duration": event.eval_duration,
        }

    if params.stream:

        async def streaming_response():
            async for event in generator:
                if await request.is_disconnected():
                    return
                elif isinstance(event, pal.events.EndEvent):
                    yield json.dumps(format_end_event(event, "")) + "\n"
                elif isinstance(event, pal.events.ChunkEvent):
                    yield json.dumps(
                        {
                            "model": params.model,
                            "created_at": datetime.now().isoformat(),
                            "message": {
                                "role": "assistant",
                                "content": event.response,
                            },
                            "done": False,
                        }
                    ) + "\n"
                else:
                    raise ValueError("Unknown event type")

        return StreamingResponse(
            streaming_response(),
            headers={
                "Transfer-Encoding": "chunked",
                "Content-Type": "application/x-ndjson",
            },
        )
    else:
        full_response = ""
        async for event in generator:
            if request is not None and await request.is_disconnected():
                raise HTTPException(status_code=499, detail="client disconnected")
            elif isinstance(event, pal.model.EndEvent):
                return format_end_event(event, full_response)
            else:
                full_response += event.response
