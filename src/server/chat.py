from datetime import datetime
import json
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, List, Dict, Any
import driver
from server.bootstrap import server
from utils import format_to_schema


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


class Request(BaseModel):
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


@server.post("/api/chat")
def chat(request: Request):

    if request.tools:
        raise HTTPException(status_code=501, detail="'tools' not implemented")

    json_schema = format_to_schema(request.format)
    prompt = ""

    generator = driver.generate(
        request.model,
        prompt,
        request.options,
        json_schema,
        request.keep_alive,
    )

    if request.stream:

        def streaming_response():
            for event in generator:
                if isinstance(event, driver.EndEvent):
                    yield format_end_event(event)
                elif isinstance(event, generator.ChunkResponse):
                    yield {
                        "model": request.model,
                        "created_at": datetime.now().isoformat(),
                        "done": False,
                        "message": Message(
                            role="assistant",
                            content=event.response,
                        ).model_dump_json(),
                    }
                else:
                    raise ValueError("Unknown event type")

        return StreamingResponse(streaming_response())
    else:
        for event in generator:
            if isinstance(event, driver.EndEvent):
                return {
                    **format_end_event(event),
                    "message": Message(
                        role="assistant",
                        content=event.full_response,
                    ).model_dump_json(),
                }


def format_end_event(event):
    return {
        "done_reason": event.done_reason,
        "done": True,
        "total_duration": event.total_duration,
        "load_duration": event.load_duration,
        "prompt_eval_count": event.prompt_eval_count,
        "prompt_eval_duration": event.prompt_eval_duration,
        "eval_count": event.eval_count,
        "eval_duration": event.eval_duration,
    }
