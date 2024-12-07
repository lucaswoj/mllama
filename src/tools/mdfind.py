import subprocess
from typing import List, Optional

from tool import tool, ToolArg
from typing import Annotated


@tool
def mdfind(
    query: Annotated[str, ToolArg("The search query")],
    limit: Annotated[int, ToolArg("The maximum number of results to return")] = 10,
    attr: Annotated[
        Optional[str], ToolArg("The attribute to fetch the value of")
    ] = None,
    onlyin: Annotated[Optional[str], ToolArg("The directory to search within")] = None,
) -> List[str]:
    """Use macOS Spotlight search to find files."""
    cmd = ["mdfind", "-0"]
    if attr:
        cmd.extend(["-attr", attr])
    if onlyin:
        cmd.extend(["-onlyin", onlyin])
    cmd.append(query)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    return result.stdout.strip("\0").split("\0")[:limit]
