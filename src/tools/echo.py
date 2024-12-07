import subprocess
from typing import List, Optional

from tool import tool, ToolArg
from typing import Annotated


@tool
def echo(input: str) -> str:
    return input
