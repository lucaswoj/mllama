import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from tool import tool

max_diff_length = 500000


def format_code_diff(diff: str) -> str:

    # Remove all lines except additions
    additions = [line[1:] for line in diff.split("\n") if line.startswith("+")]

    # Break into sections by file, limit each section to 50 lines
    sections = []
    for chunk in "\n".join(additions).split("++ b/"):
        if chunk.strip():
            lines = chunk.split("\n")
            title = lines[0]
            body = "\n".join(lines[1:51]).strip().replace("```", "\\`\\`\\`")
            ext = Path(title).suffix[1:]
            sections.append(f"### {title}\n```{ext}\n{body}\n```")

    return "\n\n".join(sections)


@tool
def git(date: str, path: str):
    end_date_object = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
    end_date = end_date_object.strftime("%Y-%m-%d")

    path = path.replace(" ", "\\ ")
    diff_command = (
        f"cd {path} && git diff --diff-filter=AM --patch --minimal -U0 "
        f"$(git rev-list -n1 --before='{date} 00:00' HEAD) "
        f"$(git rev-list -n1 --before='{end_date} 00:00' HEAD) -- . "
        f"':(exclude)Hours/*' ':(exclude)package-lock.json' | head -c {max_diff_length}"
    )
    diff = (
        subprocess.check_output(diff_command, shell=True)
        .decode("utf-8")
        .replace("```", "\\`\\`\\`")
        .strip()
    )

    if not diff:
        return ""

    commit_messages_command = f"cd {path} && git log --oneline --after='{date} 00:00' --before='{end_date} 00:00' --pretty=format:'%s'"
    commit_messages = "\n".join(
        message
        for message in (
            subprocess.check_output(commit_messages_command, shell=True)
            .decode("utf-8")
            .split("\n")
        )
        if message != "WIP" and not message.startswith("vault backup: ")
    )

    if not commit_messages:
        return diff

    return f"{commit_messages}\n\n{format_code_diff(diff)}"
