from __future__ import annotations

from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project_path(path: str | Path, project_root: str | Path | None = None) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    root = Path(project_root) if project_root is not None else get_project_root()
    return root / candidate


def create_run_dir(run_root: str | Path, model_name: str, project_root: str | Path | None = None) -> Path:
    root = resolve_project_path(run_root, project_root)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"{timestamp}_{model_name}"
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "plots").mkdir(parents=True, exist_ok=True)
    return run_dir

