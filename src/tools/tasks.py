import os
from run import run

from tool import tool


@tool
def tasks(date: str, area: str):
    path = os.path.join(os.environ["OBSIDIAN_VAULT_DIR"], area).replace(" ", "\\ ")
    command = f'grep -r "\u2705 {date}" {path} --exclude-dir=Hours || true'
    yield from run(command)
