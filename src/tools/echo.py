from tool import tool, ToolArg


@tool
def echo(input: str) -> str:
    return input
