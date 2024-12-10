from datetime import datetime
import json
from time import time_ns
from fastapi import APIRouter, HTTPException
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, List, Dict, Any
import pal
from pal.model import Model
import pal.model


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
        str | int,
        Field(
            description="controls how long the model will stay loaded into memory following the request (default: 5m)"
        ),
    ] = "5m"
    prompt: Annotated[
        Optional[str], Field(description="the prompt to generate a response for")
    ] = None
    suffix: Annotated[
        Optional[str], Field(description="the text after the model response")
    ] = None
    images: Annotated[
        Optional[List[str]],
        Field(
            description="(optional) a list of base64-encoded images (for multimodal models such as llava)"
        ),
    ] = None
    system: Annotated[
        Optional[str],
        Field(
            description="system message to (overrides what is defined in the Modelfile)"
        ),
    ] = None
    template: Annotated[
        Optional[str],
        Field(
            description="the prompt template to use (overrides what is defined in the Modelfile)"
        ),
    ] = None
    raw: Annotated[
        Optional[bool],
        Field(
            description="if true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are specifying a full templated prompt in your request to the API"
        ),
    ] = None
    context: Annotated[
        Any,
        Field(
            description="(deprecated) the context parameter returned from a previous request to /generate, this can be used to keep a short conversational memory",
        ),
    ] = None


class ChunkResponse(BaseModel):
    model: Annotated[str, Field(description="the name of the model used")]
    created_at: Annotated[
        str, Field(description="timestamp when the response was generated")
    ] = datetime.now().isoformat()
    response: Annotated[
        str,
        Field(
            description="empty if the response was streamed, if not streamed, this will contain the full response"
        ),
    ] = ""
    done: Annotated[
        bool, Field(description="true if the stream has ended, false otherwise")
    ] = False
    done_reason: Optional[str] = None


router = APIRouter()


@router.post("/api/generate")
async def generate(params: Params, request: fastapi.Request):
    if params.system:
        raise HTTPException(status_code=501, detail="'system' not implemented")

    if params.suffix:
        raise HTTPException(status_code=501, detail="'suffix' not implemented")

    if params.images:
        raise HTTPException(status_code=501, detail="'images' not implemented")

    if params.template:
        raise HTTPException(status_code=501, detail="'template' not implemented")

    if params.raw:
        raise HTTPException(status_code=501, detail="'raw' not implemented")

    if params.context:
        raise HTTPException(status_code=501, detail="'context' not implemented")

    if params.keep_alive == 0:
        Model.unload(params.model)
        return {
            "model": params.model,
            "created_at": datetime.now().isoformat(),
            "response": "",
            "done_reason": "unload",
            "done": True,
        }

    start_time = time_ns()

    model = Model.load(params.model, params.keep_alive)

    if params.prompt is None:
        return {
            "model": params.model,
            "created_at": datetime.now().isoformat(),
            "response": "",
            "done": True,
        }

    generator = model.generate(
        start_time=start_time,
        prompt=params.prompt,
        options=params.options,
        format=params.format,
    )

    def format_end_event(event):
        return {
            "model": params.model,
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
                elif isinstance(event, pal.model.EndEvent):
                    yield json.dumps(format_end_event(event)) + "\n"
                elif isinstance(event, pal.model.ChunkEvent):
                    yield json.dumps(
                        {
                            "model": params.model,
                            "created_at": datetime.now().isoformat(),
                            "response": "",
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
            if await request.is_disconnected():
                raise HTTPException(status_code=499, detail="client disconnected")
            elif isinstance(event, pal.model.EndEvent):
                return {**format_end_event(event), "response": full_response}
            else:
                full_response += event.response
