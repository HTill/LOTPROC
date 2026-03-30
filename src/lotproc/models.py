from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class NodeRecord:
    path: Tuple[str, ...]
    key: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    payload: Any = None


@dataclass(frozen=True)
class ProcessResult:
    path: Tuple[str, ...]
    output: Any = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    relative_path: Tuple[str, ...] = field(default_factory=tuple)
