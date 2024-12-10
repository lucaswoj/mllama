import os
import subprocess
from typing import Dict
from dotenv import load_dotenv
import click
import json

load_dotenv()


@click.group()
def tools():
    pass


dir = os.getenv("PAL_TOOLS")

if dir is None:
    raise RuntimeError("PAL_TOOLS environment variable is not set")


def get_name(file: str):
    return file[: file.index(".")]


executable: Dict[str, str] = {}

for file in os.listdir(dir):
    path = os.path.join(dir, file)
    if os.access(path, os.X_OK):
        executable[get_name(file)] = path

    elif file.endswith(".json"):
        name = get_name(file)

        with open(path) as f:
            schema = json.load(f)

        def command(**kwargs):
            if name not in executable:
                raise RuntimeError(
                    f"Tool for '{name}' not found. Ensure there is a file at '{os.path.join(dir, name)}'* with the executable bit set."
                )

            result = subprocess.call([executable[name], json.dumps(kwargs)])
            os.exit(result)

        for property, property_schema in schema["parameters"]["properties"].items():
            if property in schema["parameters"].get("required", []):
                command = click.argument(
                    property,
                    default=property_schema.get("default"),
                    required=True,
                )(command)
            else:
                command = click.option(
                    f"--{property}",
                    default=property_schema.get("default"),
                    help=property_schema.get("description"),
                )(command)

        tools.command(
            name=name,
            help=schema["description"],
        )(command)

tools.command()


@tools.command()
def help():
    click.echo(tools.get_help(click.Context(tools)))


# TODO take a better abort signal than fastapi_request.is_disconnected
if __name__ == "__main__":
    tools()
