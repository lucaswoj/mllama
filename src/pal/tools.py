import os
import pal.model
import shlex


import subprocess
from typing import Any


async def generate(message: str, fastapi_request: Any):
    process = subprocess.Popen(
        [
            "python",
            os.path.join(os.path.dirname(__file__), "tools_cli.py"),
            *shlex.split(message[1:]),
        ],
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
                print("aborting tool")
                process.kill()
                break
            print("tool output", line)
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
