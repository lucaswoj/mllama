from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()


class GenerateCompletionRequest(BaseModel):
    model: str
    prompt: Optional[str] = None
    suffix: Optional[str] = None
    images: Optional[List[str]] = None
    format: Optional[str] = None
    options: Optional[dict] = None
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[List[int]] = None
    stream: Optional[bool] = True
    raw: Optional[bool] = False
    keep_alive: Optional[str] = "5m"


@router.post("/api/generate")
async def generate_completion(request: GenerateCompletionRequest):
    """
    Generate a response for a given prompt with a provided model.
    """
    raise NotImplementedError()


class CreateModelRequest(BaseModel):
    model: str
    modelfile: Optional[str] = None
    stream: Optional[bool] = True
    path: Optional[str] = None
    quantize: Optional[str] = None


@router.post("/api/create")
async def create_model(request: CreateModelRequest):
    """
    Create a model from a Modelfile.
    """
    raise NotImplementedError()


@router.get("/api/tags")
async def list_local_models():
    """
    List models that are available locally.
    """
    raise NotImplementedError()


class ShowModelRequest(BaseModel):
    model: str
    verbose: Optional[bool] = False


@router.post("/api/show")
async def show_model_information(request: ShowModelRequest):
    """
    Show information about a model including details, modelfile, template, parameters, license, system prompt.
    """
    raise NotImplementedError()


class CopyModelRequest(BaseModel):
    source: str
    destination: str


@router.post("/api/copy")
async def copy_model(request: CopyModelRequest):
    """
    Copy a model. Creates a model with another name from an existing model.
    """
    raise NotImplementedError()


class DeleteModelRequest(BaseModel):
    model: str


@router.delete("/api/delete")
async def delete_model(request: DeleteModelRequest):
    """
    Delete a model and its data.
    """
    raise NotImplementedError()


class PullModelRequest(BaseModel):
    model: str
    insecure: Optional[bool] = False
    stream: Optional[bool] = True


@router.post("/api/pull")
async def pull_model(request: PullModelRequest):
    """
    Download a model from the ollama library.
    """
    raise NotImplementedError()


class PushModelRequest(BaseModel):
    model: str
    insecure: Optional[bool] = False
    stream: Optional[bool] = True


@router.post("/api/push")
async def push_model(request: PushModelRequest):
    """
    Upload a model to a model library.
    """
    raise NotImplementedError()


class GenerateEmbeddingsRequest(BaseModel):
    model: str
    input: List[str]
    truncate: Optional[bool] = True
    options: Optional[dict] = None
    keep_alive: Optional[str] = "5m"


@router.post("/api/embed")
async def generate_embeddings(request: GenerateEmbeddingsRequest):
    """
    Generate embeddings from a model.
    """
    raise NotImplementedError()


@router.get("/api/ps")
async def list_running_models():
    """
    List models that are currently loaded into memory.
    """
    raise NotImplementedError()
