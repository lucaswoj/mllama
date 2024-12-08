from datetime import datetime
import time
from functools import cache
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import outlines
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, List, Dict, Any

server = FastAPI()


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


class GenerateRequest(BaseModel):
    model: Annotated[str, Field(description="the model name")]
    prompt: Annotated[str, Field(description="the prompt to generate a response for")]
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
        Optional[str],
        Field(
            description="controls how long the model will stay loaded into memory following the request (default: 5m)"
        ),
    ] = None
    context: Annotated[
        Any,
        Field(
            deprecated="Deprecated!",
            description="the context parameter returned from a previous request to /generate, this can be used to keep a short conversational memory",
        ),
    ] = None


class GenerateStreamResponse(BaseModel):
    model: Annotated[str, Field(description="the name of the model used")]
    created_at: Annotated[
        str, Field(description="timestamp when the response was generated")
    ]
    response: Annotated[
        str,
        Field(
            description="empty if the response was streamed, if not streamed, this will contain the full response"
        ),
    ]
    done: Annotated[
        bool, Field(description="true if the stream has ended, false otherwise")
    ]


class GenerateResponse(GenerateStreamResponse):
    context: Annotated[
        Any,
        Field(
            deprecated="Deprecated!",
            description="an encoding of the conversation used in this response, this can be sent in the next request to keep a conversational memory",
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


@cache
def get_model(name: str):
    if name.startswith("mlx-community/"):
        return outlines.models.mlxlm(name)
    else:
        return outlines.models.transformers(name)


@server.post("/api/generate")
def generate(request: GenerateRequest):
    start_time = time.time_ns()

    model = get_model(request.model)

    load_time = time.time_ns()

    if request.suffix:
        raise HTTPException(status_code=501, detail="'suffix' not implemented")

    if request.images:
        raise HTTPException(status_code=501, detail="'images' not implemented")

    if request.template:
        raise HTTPException(status_code=501, detail="'template' not implemented")

    if request.raw:
        raise HTTPException(status_code=501, detail="'raw' not implemented")

    if request.keep_alive:
        raise HTTPException(status_code=501, detail="'keep_alive' not implemented")

    if set(request.options.keys()) - set(["max_tokens"]):
        raise HTTPException(
            status_code=501,
            detail=f"'options' keys '{request.options.keys()}' not implemented",
        )

    if request.format is None:
        generator = outlines.generate.text(model)
    elif request.format == "json":
        generator = outlines.generate.json(model, Dict[str, Any])
    else:
        generator = outlines.generate.json(model, request.format)

    generator_time = time.time_ns()

    def get_end(response: str):
        end_time = time.time_ns()

        return GenerateResponse(
            model=request.model,
            created_at=datetime.now().isoformat(),
            response=response,
            done=True,
            total_duration=end_time - start_time,
            load_duration=load_time - start_time,
            prompt_eval_count=0,  # TODO
            prompt_eval_duration=generator_time - load_time,
            eval_count=0,  # TODO
            eval_duration=end_time - generator_time,
        )

    if request.stream:

        def inner():
            for response in generator.stream(
                request.prompt, max_tokens=request.options["max_tokens"]
            ):
                yield GenerateStreamResponse(
                    model=request.model,
                    created_at=datetime.now().isoformat(),
                    response=response,
                    done=False,
                )

            yield get_end("")

        return StreamingResponse(inner())
    else:
        return get_end(
            generator(
                request.prompt,
                max_tokens=request.options["max_tokens"],
            )
        )


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
