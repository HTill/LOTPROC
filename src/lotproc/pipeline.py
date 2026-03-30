# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Optional, Sequence

from lotdb import BaseNode

from .buffering import buffer_iterable
from .filters import filter_key_regex, filter_nodes
from .preparation import node_to_record
from .processing import process_batches
from .targets import WriteTarget
from .traversal import iter_leaves, iter_level


class Pipeline:
    def __init__(self, source: Any):
        self._source = source
        self._steps: list[Callable[[Any], Any]] = []
        self._buffered = False
        self._writes_to: Optional[WriteTarget] = None

    @classmethod
    def from_root(cls, root: BaseNode) -> "Pipeline":
        return cls(root)

    @classmethod
    def from_iterable(cls, items: Iterable[Any]) -> "Pipeline":
        return cls(items)

    def traverse(self, strategy: str = "leaves", *, level: Any = "deepest") -> "Pipeline":
        def step(source: Any):
            if strategy == "leaves":
                return iter_leaves(source)
            if strategy == "level":
                return iter_level(source, level=level)
            raise ValueError("strategy must be 'leaves' or 'level'.")

        self._steps.append(step)
        return self

    def filter(self, predicate: Callable[[Any], bool]) -> "Pipeline":
        self._steps.append(lambda nodes: filter_nodes(nodes, predicate))
        return self

    def filter_key(self, pattern: str, *, invert: bool = False) -> "Pipeline":
        self._steps.append(lambda nodes: filter_key_regex(nodes, pattern, invert=invert))
        return self

    def buffer(self, size: int) -> "Pipeline":
        self._steps.append(lambda items: buffer_iterable(items, size))
        self._buffered = True
        return self

    def prepare(
        self,
        fn: Optional[Callable[[Any], Any]] = None,
        *,
        attribute_names: Optional[Sequence[str]] = None,
        include_all_attributes: bool = False,
    ) -> "Pipeline":
        prepare_fn = fn or (
            lambda node: node_to_record(
                node,
                attribute_names=attribute_names,
                include_all_attributes=include_all_attributes,
            )
        )

        if self._buffered:
            self._steps.append(lambda batches: ([prepare_fn(item) for item in batch] for batch in batches))
        else:
            self._steps.append(lambda items: (prepare_fn(item) for item in items))

        return self

    def process(
        self,
        processor: Callable[[Any], Any],
        *,
        mode: str = "sync",
        workers: Optional[int] = None,
    ) -> "Pipeline":
        if mode == "process" and not self._buffered:
            raise ValueError("Multiprocessing requires buffered batches before process(...).")

        if self._buffered:
            self._steps.append(lambda batches: process_batches(batches, processor, mode=mode, workers=workers))
        else:
            self._steps.append(
                lambda items: process_batches(([item] for item in items), processor, mode=mode, workers=workers)
            )

        return self

    def write(self, target: WriteTarget) -> "Pipeline":
        self._writes_to = target
        return self

    def run(self):
        data = self._source
        for step in self._steps:
            data = step(data)

        if self._writes_to is not None:
            self._writes_to.write_many(data)
            return self._writes_to

        return list(data)
