import os
from pal.logger import logger
import pal.model
import shlex


import subprocess
from typing import Any


async def generate(message: str, fastapi_request: Any):
    args = [
        "venv/bin/python",
        os.path.join(os.path.dirname(__file__), "tools_cli.py"),
        *shlex.split(message[1:]),
    ]
    name = args[2]

    logger.info(f"tool - {name} - start with args: {args[3:]}")
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if process.stdout is None:
        raise RuntimeError("Process has no stdout")

    full_response = ""

    try:
        for line in iter(process.stdout.readline, ""):
            if await fastapi_request.is_disconnected():
                logger.warning(f"tool - {args[2]} - killing process")
                process.kill()
                break
            yield pal.model.ChunkEvent(
                response=line + "\n",
            )
            full_response += line + "\n"
    finally:
        process.stdout.close()
        process.wait()
        yield pal.model.EndEvent(
            full_response=full_response,
            done_reason=None,
            total_duration=0,
            load_duration=0,
            prompt_eval_count=0,
            prompt_eval_duration=0,
            eval_count=0,
            eval_duration=0,
        )
        logger.info(f"tool - {name} - end")
