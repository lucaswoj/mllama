import subprocess
import logging


def shell(cmd: str):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,  # Ensures the output is returned as a string
        shell=True,  # Use the shell to execute the command string
    )
    if process.stdout is None:
        raise RuntimeError("Process has no stdout")
    try:
        # Stream the output line by line
        for line in iter(process.stdout.readline, ""):
            yield line
    finally:
        process.stdout.close()
        process.wait()


logger = logging.getLogger("pal")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)-10s %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
