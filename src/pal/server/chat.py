from datetime import datetime
import json
from fastapi import HTTPException
import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, List, Dict, Any
import pal
from pal.server.bootstrap import server
from transformers import AutoTokenizer
from pal.utils import ollama_format_to_json_schema
import pal.generate


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
async def chat(request: Request, fastapi_request: fastapi.Request):

    if request.tools:
        raise HTTPException(status_code=501, detail="'tools' not implemented")

    json_schema = ollama_format_to_json_schema(request.format)

    tokenizer = AutoTokenizer.from_pretrained(request.model)
    stop_strings: list[str] = [tokenizer.eos_token, "<|im_end|>"]

    if tokenizer.chat_template is not None:
        pass
    elif request.model.startswith("mlx-community/llama3.3"):
        stop_strings = ["<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>"]
        tokenizer.chat_template = open("./chat_templates/llama3.3.jinja").read()
    else:
        tokenizer.chat_template = open("./chat_templates/chatml.jinja").read()

    prompt = tokenizer.apply_chat_template(
        conversation=request.messages, tokenize=False, add_generation_prompt=True
    )

    generator = pal.generate.generate(
        model=request.model,
        prompt=prompt,
        options=request.options,
        json_schema=json_schema,
        keep_alive=request.keep_alive,
        stop_strings=stop_strings,
    )

    if request.stream:

        async def streaming_response():
            for event in generator:
                if (
                    fastapi_request is not None
                    and await fastapi_request.is_disconnected()
                ):
                    return
                elif isinstance(event, pal.generate.EndEvent):
                    yield json.dumps(format_end_event(event))
                elif isinstance(event, pal.generate.ChunkEvent):
                    yield json.dumps(
                        {
                            "model": request.model,
                            "created_at": datetime.now().isoformat(),
                            "message": {
                                "role": "assistant",
                                "content": event.response,
                            },
                            "done": False,
                        }
                    )
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
        for event in generator:
            if fastapi_request is not None and await fastapi_request.is_disconnected():
                return HTTPException(status_code=499, detail="client disconnected")
            elif isinstance(event, pal.generate.EndEvent):
                return {
                    **format_end_event(event),
                    "message": {
                        "role": "assistant",
                        "content": event.full_response,
                    },
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