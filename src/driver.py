from datetime import datetime, timedelta
import threading
import time
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from time import time_ns
import mlx_engine.model_kit
import mlx_engine.vision
import mlx_engine.vision.vision_model_kit
import mlx_engine.model_kit
import mlx_engine.vision.vision_model_kit
import huggingface_hub
from utils import logger


from datetime import datetime
from typing import Dict, Tuple


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
        path = huggingface_hub.snapshot_download(name, local_files_only=True)
        if path is None:
            raise HTTPException(status_code=404, detail=f"Model {name} not found")

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


class ChunkEvent(BaseModel):
    response: str


class UnloadEvent(BaseModel):
    pass


class LoadEvent(BaseModel):
    pass


class EndEvent(UnloadEvent):
    done_reason: Optional[str]
    full_response: str
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


def generate(
    model: str,
    prompt: Optional[str],
    options: Dict[str, Any],
    json_schema: Optional[str],
    keep_alive: str,
    stop_strings: Optional[List[str]],
):
    if keep_alive == 0:
        unload_model(model)
        return UnloadEvent()

    start_time = time_ns()

    model_obj = load_model(model, keep_alive)

    if prompt is None:
        return LoadEvent()

    load_time = time_ns()

    tokens = mlx_engine.tokenize(model_obj, prompt)

    prompt_eval_time = time_ns()

    eval_time = time_ns()

    generator = mlx_engine.create_generator(
        model_obj,
        tokens,
        images_b64=None,
        json_schema=json_schema,
        max_tokens=(options["max_tokens"] if "max_tokens" in options else 1024),
        repetition_context_size=20,
        repetition_penalty=1.1,
        seed=None,
        temp=0.7,
        top_p=None,
        min_tokens_to_keep=None,
        stop_strings=stop_strings,
    )

    done_reason = None
    full_response = ""
    for response_chunk in generator:
        chunk_event = ChunkEvent(
            response=response_chunk.text,
        )
        yield chunk_event
        full_response += response_chunk.text
        if response_chunk.stop_condition:
            done_reason = response_chunk.stop_condition.stop_reason
            break

    end_time = time_ns()
    end_event = EndEvent(
        full_response=full_response,
        total_duration=end_time - start_time,
        load_duration=load_time - start_time,
        prompt_eval_count=len(tokens),
        prompt_eval_duration=prompt_eval_time - load_time,
        eval_count=0,
        eval_duration=end_time - eval_time,
        done_reason=done_reason,
    )
    logger.debug(end_event)
    yield end_event
