#!/usr/bin/env /Users/lucaswoj/Code/pal/venv/bin/python

from functools import wraps
import importlib
import pkgutil
from pprint import pformat
from typing import Annotated, get_type_hints
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import inspect
import typer
from tool import ToolArg
from dotenv import load_dotenv

load_dotenv("/Users/lucaswoj/Code/pal/.env")

app = typer.Typer()


def add_command(value):
    @app.command()
    @wraps(value)
    def wrapper(*args, **kwargs):
        output = value(*args, **kwargs)
        if inspect.isgenerator(output):
            for item in output:
                print(item, end="")
        else:
            formatted_text = pformat(output)
            colorful_text = highlight(
                formatted_text, PythonLexer(), TerminalFormatter()
            )
            print(colorful_text, end="")

    signature = inspect.signature(value, eval_str=True)

    type_hints = get_type_hints(value, include_extras=True)

    for param in signature.parameters.values():
        param_hints = type_hints[param.name]
        if hasattr(param_hints, "__metadata__"):
            for annotation in param_hints.__metadata__:
                if isinstance(annotation, ToolArg) and param.default is not param.empty:
                    wrapper.__annotations__[param.name] = Annotated[
                        param_hints,
                        typer.Option(help=annotation.description),
                    ]
                elif isinstance(annotation, ToolArg):
                    wrapper.__annotations__[param.name] = Annotated[
                        param_hints,
                        typer.Argument(help=annotation.description),
                    ]


visited = set()

for module_info in pkgutil.iter_modules(importlib.import_module(f"tools").__path__):
    module = importlib.import_module(f"tools.{module_info.name}")
    for name, value in inspect.getmembers(module):
        if (
            inspect.isfunction(value)
            and getattr(value, "is_tool", False)
            and value not in visited
        ):
            visited.add(value)
            add_command(value)

app()