from functools import wraps


def tool(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.is_tool = True

    return wrapper


class ToolArg:
    def __init__(self, description: str):
        self.description = description
