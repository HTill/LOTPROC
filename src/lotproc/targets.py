# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from lotdb import BaseNode

from .models import ProcessResult
from .write_policies import BaseWritePolicy, FreshDatabaseWritePolicy, InlineWritePolicy, MirrorWritePolicy


def _normalize_path(parts: Sequence[str]) -> list[str]:
    return [str(part) for part in parts if str(part)]


def _ensure_node(root: BaseNode, path: Sequence[str]) -> BaseNode:
    normalized = _normalize_path(path)

    if not normalized:
        return root

    return root.gns(normalized)


def _set_attribute(node: BaseNode, key: str, value: Any) -> None:
    node.set_attribute(key, value)


def flatten_results(results: Iterable[Any]) -> Iterator[ProcessResult]:
    for result in results:
        if isinstance(result, ProcessResult):
            yield result
        elif isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict)):
            for nested in flatten_results(result):
                yield nested
        else:
            raise TypeError("Processor results must be ProcessResult instances or iterables of them.")


@dataclass
class WriteTarget:
    root: BaseNode
    policy: BaseWritePolicy
    output_attribute: Optional[str] = "result"
    written_paths: list[tuple[str, ...]] = field(default_factory=list)

    def target_path(self, result: ProcessResult) -> tuple[str, ...]:
        return self.policy.target_path(result)

    def write(self, result: ProcessResult) -> BaseNode:
        node = _ensure_node(self.root, self.target_path(result))

        if self.output_attribute is not None:
            _set_attribute(node, self.output_attribute, result.output)

        for key, value in result.attributes.items():
            _set_attribute(node, key, value)

        self.written_paths.append(tuple(self.target_path(result)))
        return node

    def write_many(self, results: Iterable[Any]) -> list[Any]:
        return [self.write(result) for result in flatten_results(results)]


@dataclass
class BaseTarget(WriteTarget):
    pass


@dataclass(init=False)
class InlineTarget(BaseTarget):
    base_path: tuple[str, ...] = ("_proc",)

    def __init__(
        self,
        root: BaseNode,
        output_attribute: Optional[str] = "result",
        base_path: tuple[str, ...] = ("_proc",),
    ) -> None:
        super().__init__(root=root, policy=InlineWritePolicy(base_path=base_path), output_attribute=output_attribute)
        self.base_path = base_path


@dataclass(init=False)
class MirrorTarget(BaseTarget):
    base_path: tuple[str, ...] = ()

    def __init__(
        self,
        root: BaseNode,
        output_attribute: Optional[str] = "result",
        base_path: tuple[str, ...] = (),
    ) -> None:
        super().__init__(root=root, policy=MirrorWritePolicy(base_path=base_path), output_attribute=output_attribute)
        self.base_path = base_path


@dataclass(init=False)
class NewDatabaseTarget(MirrorTarget):
    def __init__(
        self,
        root: BaseNode,
        output_attribute: Optional[str] = "result",
        base_path: tuple[str, ...] = (),
    ) -> None:
        BaseTarget.__init__(
            self,
            root=root,
            policy=FreshDatabaseWritePolicy(base_path=base_path),
            output_attribute=output_attribute,
        )
        self.base_path = base_path
