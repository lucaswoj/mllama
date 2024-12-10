from datetime import datetime, timedelta
import json
import threading
import time
from typing import List, Literal
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from time import time_ns
import mlx_engine.model_kit
import mlx_engine.vision
import mlx_engine.vision.vision_model_kit
import huggingface_hub
from datetime import datetime
from typing import Dict


class ChunkEvent(BaseModel):
    response: str


class EndEvent(BaseModel):
    full_response: str
    done_reason: Optional[str]
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


class Model:

    @staticmethod
    def load(name: str, keep_alive: str | int):
        """Loads a model into the cache or extends its expiration."""
        if isinstance(keep_alive, str) and keep_alive.endswith("m"):
            delta = timedelta(minutes=int(keep_alive[:-1]))
        else:
            raise ValueError(f"Invalid keep_alive value: {keep_alive}")

        if name not in cache:
            cache[name] = Model(name, expiration=datetime.now() + delta)

        model = cache[name]
        model.expiration = max(model.expiration, datetime.now() + delta)
        return model

    @staticmethod
    def unload(name: str):
        """Unloads a model from the cache."""
        if name in cache:
            del cache[name]

    name: str
    model: (
        mlx_engine.model_kit.ModelKit
        | mlx_engine.vision.vision_model_kit.VisionModelKit
    )
    expiration: datetime
    stop_strings: List[str]

    def __init__(
        self,
        name: str,
        expiration: datetime,
    ):
        self.name = name
        self.expiration = expiration

        path = huggingface_hub.snapshot_download(name, local_files_only=True)
        if path is None:
            raise HTTPException(status_code=404, detail=f"Model {name} not found")

        self.model = mlx_engine.load_model(
            path, max_kv_size=4096, trust_remote_code=False
        )

        tokenizer = self.model.tokenizer

        if tokenizer.chat_template is not None:
            pass
        else:
            tokenizer.chat_template = open("src/pal/chat_templates/chatml.jinja").read()

        if name.startswith("mlx-community/llama3.3") or name.startswith("Qwen/"):
            self.stop_strings = ["<|im_end|>"]
        elif tokenizer.eos_token is not None:
            self.stop_strings = [tokenizer.eos_token]
        else:
            self.stop_strings = ["<|im_end|>"]

    def template(self, **kwargs):
        return self.model.tokenizer.apply_chat_template(
            tokenize=False, add_generation_prompt=True, **kwargs
        )

    async def generate(
        self,
        start_time: int,
        prompt: Optional[str],
        options: Dict[str, Any],
        format: Literal["json"] | Dict[str, Any] | None,
    ):
        load_time = time_ns()

        tokens = mlx_engine.tokenize(self.model, prompt)

        if format == "json":
            json_schema = '{"type": "object", "additionalProperties": true}'
        elif format is not None:
            json_schema = json.dumps(format)
        else:
            json_schema = None

        generator = mlx_engine.create_generator(
            self.model,
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
            stop_strings=self.stop_strings,
        )

        prompt_eval_time = None
        done_reason = None
        full_response = ""
        eval_count = 0

        for response_chunk in generator:
            if prompt_eval_time is None:
                prompt_eval_time = time_ns()
            yield ChunkEvent(
                response=response_chunk.text,
            )
            eval_count += 1
            full_response += response_chunk.text
            if response_chunk.stop_condition:
                done_reason = response_chunk.stop_condition.stop_reason
                break

        end_time = time_ns()
        yield EndEvent(
            full_response=full_response,
            total_duration=end_time - start_time,
            load_duration=load_time - start_time,
            prompt_eval_count=len(tokens),
            prompt_eval_duration=(
                prompt_eval_time - load_time if prompt_eval_time else 0
            ),
            eval_count=eval_count,
            eval_duration=end_time - prompt_eval_time if prompt_eval_time else 0,
            done_reason=done_reason,
        )


cache: Dict[str, Model] = {}


def clean_cache():
    """Periodically checks and removes expired models from the cache."""
    while True:
        now = datetime.now()
        for model in list(cache.values()):
            if model.expiration < now:
                Model.unload(model.name)
        time.sleep(10)  # Run the cleanup every 10 seconds


clean_model_cache_thread = threading.Thread(target=clean_cache, daemon=True)
clean_model_cache_thread.start()
