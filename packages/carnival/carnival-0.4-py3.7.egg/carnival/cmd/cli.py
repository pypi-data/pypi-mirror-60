from carnival.core.utils import run_command


def run(command: str, **kwargs):
    return run_command(command, **kwargs)


def pty(command: str, **kwargs):
    return run(command, pty=True, **kwargs)


def mkdirs(*dirs: str):
    return [run(f"mkdir -p {x}") for x in dirs]
