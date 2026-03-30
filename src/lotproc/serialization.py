# pyright: reportMissingImports=false

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any


def save_to_file(obj: Any, path: str | Path | None = None) -> None:
    target = Path("saved_obj" if path is None else path).with_suffix(".pyobj")
    with target.open(mode="wb") as file_handle:
        pickle.dump(obj, file_handle)


def load_from_file(path: str | Path) -> Any:
    with Path(path).open(mode="rb") as file_handle:
        return pickle.load(file_handle)
