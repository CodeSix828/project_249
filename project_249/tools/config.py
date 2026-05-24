import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKDIR_ROOT = str(PROJECT_ROOT / "data") + os.sep

os.makedirs(WORKDIR_ROOT, exist_ok=True)

ALLOWED_EXTERNAL_PATHS: list[str] = []
