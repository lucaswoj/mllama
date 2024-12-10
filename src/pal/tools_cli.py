import os
import subprocess
import sys
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


def add_command(file: str):
    name = get_name(file)

    with open(path) as f:
        schema = json.load(f)

    def command(**kwargs):
        if name not in executable:
            raise RuntimeError(
                f"Check that '{os.path.join(dir, name)}.*' exists and is executable (chmod +x)"
            )

        result = subprocess.call([executable[name], json.dumps(kwargs)])
        sys.exit(result)

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


executable: Dict[str, str] = {}

for file in os.listdir(dir):
    path = os.path.join(dir, file)
    if os.access(path, os.X_OK):
        executable[get_name(file)] = path

    elif file.endswith(".json"):
        add_command(file)


@tools.command()
def help():
    click.echo(tools.get_help(click.Context(tools)))


if __name__ == "__main__":
    tools()
