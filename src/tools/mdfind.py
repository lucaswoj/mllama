import subprocess
from typing import List, Optional

from tool import tool, ToolArg
from typing import Annotated


@tool
def mdfind(
    query: Annotated[str, ToolArg("The search query")],
    attr: Annotated[
        Optional[str], ToolArg("The attribute to fetch the value of")
    ] = None,
    onlyin: Annotated[Optional[str], ToolArg("The directory to search within")] = None,
) -> str:
    """Use macOS Spotlight search to find files."""
    cmd = ["mdfind"]
    if attr:
        cmd.extend(["-attr", attr])
    if onlyin:
        cmd.extend(["-onlyin", onlyin])
    cmd.append(query)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,  # Ensures the output is returned as a string
    )
    try:
        # Stream the output line by line
        for line in iter(process.stdout.readline, ""):
            yield line
    finally:
        process.stdout.close()
        process.wait()  # Ensure the process finishes
