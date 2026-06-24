import subprocess
import sys
from pathlib import Path

base = Path(__file__).resolve().parent
python = base / ".venv" / "Scripts" / "python.exe"
out = base / "server.out.log"
err = base / "server.err.log"

with out.open("ab", buffering=0) as stdout, err.open("ab", buffering=0) as stderr:
    subprocess.Popen(
        [
            str(python),
            "-m",
            "uvicorn",
            "app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=str(base),
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=stderr,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )

sys.exit(0)
