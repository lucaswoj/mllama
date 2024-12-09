from typing import Optional
from tool import tool, ToolArg
from typing import Annotated
from utils import shell


@tool
def spotlight(
    query: Annotated[str, ToolArg("The search query")],
    attr: Annotated[
        Optional[str], ToolArg("The attribute to fetch the value of")
    ] = None,
    onlyin: Annotated[Optional[str], ToolArg("The directory to search within")] = None,
):
    """Use macOS Spotlight search to find files."""

    cmd = "mdfind"
    if attr:
        cmd += f" -attr {attr}"
    if onlyin:
        cmd += f" -onlyin {onlyin}"
    cmd += f" {query}"

    yield from shell(cmd)
