from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
import huggingface_hub
from pal.server.bootstrap import server

import pal.server.chat as chat  # noqa
import pal.server.tags as tags  # noqa
import pal.server.generate as generate  # noqa


@server.get("/")
@server.head("/")
def root():
    return "Pal is running"


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
    # tool_calls: List[Tool] = []


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


class PullRequest(BaseModel):
    model: str
    insecure: Optional[bool] = False
    stream: Optional[bool] = True


@server.post("/api/pull")
def pull(request: PullRequest):
    huggingface_hub.snapshot_download(request.model)
    return {"status": "success"}


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
