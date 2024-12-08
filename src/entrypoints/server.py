from datetime import datetime, timedelta
import json
import threading
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, List, Dict, Any, Tuple
import mlx_engine
import huggingface_hub
import mlx_engine.model_kit
import mlx_engine.vision
import mlx_engine.vision.vision_model_kit

server = FastAPI()


model_cache: Dict[
    str,
    Tuple[
        (
            mlx_engine.model_kit.ModelKit
            | mlx_engine.vision.vision_model_kit.VisionModelKit
        ),
        datetime,
    ],
] = {}


def load_model(name: str, keep_alive: str):
    """Loads a model into the cache or extends its expiration."""
    if keep_alive.endswith("m"):
        delta = timedelta(minutes=int(keep_alive[:-1]))
    else:
        raise ValueError(f"Invalid keep_alive value: {keep_alive}")

    if name not in model_cache:
        path = huggingface_hub.snapshot_download(repo_id=name)
        model = mlx_engine.load_model(path, max_kv_size=4096, trust_remote_code=False)
        model_cache[name] = (model, datetime.now() + delta)
    else:
        model, prev_exp = model_cache[name]
        # Extend expiration time to ensure it stays in cache if accessed
        model_cache[name] = (
            model,
            max(prev_exp, datetime.now() + delta),
        )
    return model


def unload_model(name: str):
    """Unloads a model from the cache."""
    if name in model_cache:
        del model_cache[name]


def clean_model_cache():
    """Periodically checks and removes expired models from the cache."""
    while True:
        now = datetime.now()
        expired_models = [name for name, (_, exp) in model_cache.items() if exp < now]
        for name in expired_models:
            unload_model(name)
        time.sleep(10)  # Run the cleanup every 10 seconds


clean_model_cache_thread = threading.Thread(target=clean_model_cache, daemon=True)
clean_model_cache_thread.start()


class GenerateRequest(BaseModel):
    model: Annotated[str, Field(description="the model name")]
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
    stream: Annotated[
        bool,
        Field(
            description="if false the response will be returned as a single response object, rather than a stream of objects"
        ),
    ] = True
    raw: Annotated[
        Optional[bool],
        Field(
            description="if true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are specifying a full templated prompt in your request to the API"
        ),
    ] = None
    keep_alive: Annotated[
        str,
        Field(
            description="controls how long the model will stay loaded into memory following the request (default: 5m)"
        ),
    ] = "5m"
    context: Annotated[
        Any,
        Field(
            description="(deprecated) the context parameter returned from a previous request to /generate, this can be used to keep a short conversational memory",
        ),
    ] = None


class GenerateResponse(BaseModel):
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


class GenerateEndResponse(GenerateResponse):
    context: Annotated[
        Any,
        Field(
            description="(deprecated) an encoding of the conversation used in this response, this can be sent in the next request to keep a conversational memory",
        ),
    ] = None
    total_duration: Annotated[
        int, Field(description="time spent generating the response (in nanoseconds)")
    ]
    load_duration: Annotated[
        int, Field(description="time spent in nanoseconds loading the model")
    ]
    prompt_eval_count: Annotated[
        int, Field(description="number of tokens in the prompt")
    ]
    prompt_eval_duration: Annotated[
        int, Field(description="time spent in nanoseconds evaluating the prompt")
    ]
    eval_count: Annotated[int, Field(description="number of tokens in the response")]
    eval_duration: Annotated[
        int, Field(description="time in nanoseconds spent generating the response")
    ]


@server.post("/api/generate")
def generate(request: GenerateRequest):
    start_time = time.time_ns()

    if request.suffix:
        raise HTTPException(status_code=501, detail="'suffix' not implemented")

    if request.images:
        raise HTTPException(status_code=501, detail="'images' not implemented")

    if request.template:
        raise HTTPException(status_code=501, detail="'template' not implemented")

    if request.raw:
        raise HTTPException(status_code=501, detail="'raw' not implemented")

    if set(request.options.keys()) - set(["max_tokens"]):
        raise HTTPException(
            status_code=501,
            detail=f"'options' keys '{request.options.keys()}' not implemented",
        )

    if request.keep_alive == 0:
        unload_model(request.model)
        return GenerateResponse(model=request.model, done_reason="unload")

    model = load_model(request.model, request.keep_alive)

    if request.prompt is None:
        return GenerateResponse(model=request.model, response="")

    load_time = time.time_ns()

    tokens = mlx_engine.tokenize(
        model,
        request.prompt,
    )

    prompt_eval_time = time.time_ns()

    json_schema = None
    if request.format == "json":
        json_schema = '{"type": "object", "additionalProperties": true}'
    elif request.format is not None:
        json_schema = json.dumps(request.format)

    generator = mlx_engine.create_generator(
        model,
        tokens,
        max_tokens=request.options["max_tokens"],
        json_schema=json_schema,
    )

    eval_time = time.time_ns()

    def get_end_response(response: str, done_reason: Optional[str] = None):
        end_time = time.time_ns()

        return GenerateEndResponse(
            model=request.model,
            response=response,
            done=True,
            total_duration=end_time - start_time,
            load_duration=load_time - start_time,
            prompt_eval_count=len(tokens),
            prompt_eval_duration=prompt_eval_time - load_time,
            eval_count=0,
            eval_duration=end_time - eval_time,
            done_reason=done_reason,
        )

    if request.stream:

        def inner():
            for response in generator:
                yield GenerateResponse(
                    model=request.model,
                    response=response.text,
                )

            yield get_end_response("")

        return StreamingResponse(inner())
    else:
        response = ""
        for response_chunk in generator:
            response += response_chunk.text
            if response_chunk.stop_condition:
                return get_end_response(
                    response, response_chunk.stop_condition.stop_reason
                )
        return get_end_response(response)


class ToolFunctionParameter(BaseModel):
    type: str
    description: Optional[str]
    enum: Optional[List[str]]
    required: Optional[List[str]]
    properties: Optional[Dict[str, "ToolFunctionParameter"]]


class ToolFunction(BaseModel):
    name: str
    description: Optional[str]
    parameters: ToolFunctionParameter


class Tool(BaseModel):
    type: str
    function: ToolFunction


class Message(BaseModel):
    role: str
    content: Optional[str]
    images: Optional[List[str]]
    tool_calls: Optional[List[Tool]]


class ChatRequest(BaseModel):
    # uses `model:tag` format
    model: str
    messages: List[Message]
    tools: Optional[List[Tool]]
    format: Optional[str]
    options: Optional[Dict[str, Any]]
    stream: Optional[bool]
    keep_alive: Optional[str]


class ChatResponse(BaseModel):
    # uses `model:tag` format
    model: str
    created_at: str
    message: Message
    done: bool

    # Measured in nanoseconds
    total_duration: Optional[int]

    # Measured in nanoseconds
    load_duration: Optional[int]
    prompt_eval_count: Optional[int]

    # Measured in nanoseconds
    prompt_eval_duration: Optional[int]
    eval_count: Optional[int]

    # Measured in nanoseconds
    eval_duration: Optional[int]


@server.post("/api/chat", response_model=ChatResponse)
def generate_chat_Generate(request: ChatRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class CreateModelRequest(BaseModel):
    # uses `model:tag` format
    model: str
    modelfile: Optional[str]
    stream: Optional[bool]
    path: Optional[str]
    quantize: Optional[str]


class CreateModelResponse(BaseModel):
    status: str


@server.post("/api/create", response_model=CreateModelResponse)
def create_model(request: CreateModelRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class ListLocalModelsResponse(BaseModel):
    models: List[Dict[str, Any]]


@server.get("/api/tags", response_model=ListLocalModelsResponse)
def list_local_models():
    raise HTTPException(status_code=501, detail="Not implemented")


class ShowModelInformationRequest(BaseModel):
    # uses `model:tag` format
    model: str
    verbose: Optional[bool]


class ShowModelInformationResponse(BaseModel):
    modelfile: str
    parameters: str
    template: str
    details: Dict[str, Any]
    model_info: Dict[str, Any]


@server.post("/api/show", response_model=ShowModelInformationResponse)
def show_model_information(request: ShowModelInformationRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class CopyModelRequest(BaseModel):
    source: str
    destination: str


class CopyModelResponse(BaseModel):
    status: str


@server.post("/api/copy", response_model=CopyModelResponse)
def copy_model(request: CopyModelRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class DeleteModelRequest(BaseModel):
    # uses `model:tag` format
    model: str


class DeleteModelResponse(BaseModel):
    status: str


@server.delete("/api/delete", response_model=DeleteModelResponse)
def delete_model(request: DeleteModelRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class PullModelRequest(BaseModel):
    # uses `model:tag` format
    model: str
    insecure: Optional[bool]
    stream: Optional[bool]


class PullModelResponse(BaseModel):
    status: str


@server.post("/api/pull", response_model=PullModelResponse)
def pull_model(request: PullModelRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class PushModelRequest(BaseModel):
    # uses `model:tag` format
    model: str
    insecure: Optional[bool]
    stream: Optional[bool]


class PushModelResponse(BaseModel):
    status: str


@server.post("/api/push", response_model=PushModelResponse)
def push_model(request: PushModelRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class GenerateEmbeddingsRequest(BaseModel):
    # uses `model:tag` format
    model: str
    input: List[str]
    truncate: Optional[bool]
    options: Optional[Dict[str, Any]]
    keep_alive: Optional[str]


class GenerateEmbeddingsResponse(BaseModel):
    # uses `model:tag` format
    model: str
    embeddings: List[List[float]]

    # Measured in nanoseconds
    total_duration: Optional[int]

    # Measured in nanoseconds
    load_duration: Optional[int]
    prompt_eval_count: Optional[int]


@server.post("/api/embed", response_model=GenerateEmbeddingsResponse)
def generate_embeddings(request: GenerateEmbeddingsRequest):
    raise HTTPException(status_code=501, detail="Not implemented")


class ListRunningModelsResponse(BaseModel):
    models: List[Dict[str, Any]]


@server.get("/api/ps", response_model=ListRunningModelsResponse)
def list_running_models():
    raise HTTPException(status_code=501, detail="Not implemented")
