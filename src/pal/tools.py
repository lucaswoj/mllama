import asyncio
import os
import shlex
from typing import Any
from fastapi import HTTPException
from pal.events import ChunkEvent, EndEvent
from pal.logger import logger


async def generate(message: str, fastapi_request: Any):
    args = [
        "venv/bin/python",
        os.path.join(os.path.dirname(__file__), "tools_cli.py"),
        *shlex.split(message[1:]),
    ]
    name = args[2]

    logger.info(f"tool - {name} - start with args: {args[3:]}")

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    if process.stdout is None:
        raise RuntimeError("Process has no stdout")

    try:
        while True:
            line = await process.stdout.readline()
            if line == b"":  # EOF reached
                break

            if await fastapi_request.is_disconnected():
                logger.warning(f"tool - {name} - killing process")
                process.kill()
                raise HTTPException(status_code=499, detail="client disconnected")

            yield ChunkEvent(response=line.decode() + "\n")
    finally:
        await process.wait()
        yield EndEvent()
        logger.info(f"tool - {name} - end")
