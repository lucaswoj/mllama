import subprocess


def run(cmd: str):
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
