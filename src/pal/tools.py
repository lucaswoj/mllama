import os

from fastapi import HTTPException
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

    try:
        for line in iter(process.stdout.readline, ""):
            if await fastapi_request.is_disconnected():
                logger.warning(f"tool - {args[2]} - killing process")
                process.kill()
                raise HTTPException(status_code=499, detail="client disconnected")
            yield pal.model.ChunkEvent(
                response=line + "\n",
            )
    finally:
        process.stdout.close()
        process.wait()
        yield pal.model.EndEvent()
        logger.info(f"tool - {name} - end")
