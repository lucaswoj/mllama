from functools import wraps
import importlib
import pkgutil
from pprint import pformat
from typing import Annotated, get_args, get_origin, get_type_hints
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import inspect
import typer
from tool import ArgDescription

app = typer.Typer()


def cpprint(obj):
    formatted_text = pformat(obj)
    colorful_text = highlight(formatted_text, PythonLexer(), TerminalFormatter())
    print(colorful_text, end="")


def add_command(value):
    @wraps(value)
    def wrapper(*args, **kwargs):
        cpprint(value(*args, **kwargs))

    for name, annotations in get_type_hints(value, include_extras=True).items():
        if hasattr(annotations, "__metadata__"):
            for annotation in annotations.__metadata__:
                if isinstance(annotation, ArgDescription):
                    wrapper.__annotations__[name] = Annotated[
                        annotations,
                        typer.Argument(help=annotation.description),
                    ]

    app.command()(wrapper)


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
