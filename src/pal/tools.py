import os
import subprocess
from dotenv import load_dotenv
import click
import json
from typing import Any, Dict, Callable, get_type_hints

load_dotenv()


@click.group()
def app():
    pass


dir = os.getenv("PAL_TOOLS")

if dir is None:
    raise RuntimeError("PAL_TOOLS environment variable is not set")

for file in os.listdir(dir):
    if file.endswith(".json"):
        name = file[: len(".json")]

        with open(os.path.join(dir, file)) as f:
            schema = json.load(f)

        def command():
            process = subprocess.Popen(
                os.path.join(dir, name + ".tsx"),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if process.stdout is None:
                raise RuntimeError("Process has no stdout")
            try:
                for line in iter(process.stdout.readline, ""):
                    print(line, end="")
            finally:
                process.stdout.close()
                process.wait()

        for property, property_schema in schema["parameters"]["properties"].items():
            if property in schema["required"]:
                command = click.argument(
                    property,
                    default=property_schema["default"],
                    help=property_schema["description"],
                )(command)
            else:
                command = click.option(
                    f"--{property}",
                    default=property_schema["default"],
                    help=property_schema["description"],
                )(command)

        app.command(
            name=name,
            help=schema["description"],
        )(command)


if __name__ == "__main__":
    app()
