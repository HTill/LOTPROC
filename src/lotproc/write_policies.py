# pyright: reportMissingImports=false

from __future__ import annotations

from dataclasses import dataclass

from .models import ProcessResult


@dataclass(frozen=True)
class BaseWritePolicy:
    def target_path(self, result: ProcessResult) -> tuple[str, ...]:
        raise NotImplementedError


@dataclass(frozen=True)
class InlineWritePolicy(BaseWritePolicy):
    base_path: tuple[str, ...] = ("_proc",)

    def target_path(self, result: ProcessResult) -> tuple[str, ...]:
        return tuple(result.path) + tuple(self.base_path) + tuple(result.relative_path)


@dataclass(frozen=True)
class MirrorWritePolicy(BaseWritePolicy):
    base_path: tuple[str, ...] = ()

    def target_path(self, result: ProcessResult) -> tuple[str, ...]:
        return tuple(self.base_path) + tuple(result.path) + tuple(result.relative_path)


@dataclass(frozen=True)
class FreshDatabaseWritePolicy(MirrorWritePolicy):
    pass
