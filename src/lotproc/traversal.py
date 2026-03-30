# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Iterator
from typing import Union

from lotdb import BaseNode


def iter_children(node: BaseNode) -> list[BaseNode]:
    return list(node.all_nodes())


def iter_leaves(node: BaseNode) -> Iterator[BaseNode]:
    yield from node.iterate_tree_leaves()


def iter_level(node: BaseNode, level: Union[int, str] = "deepest") -> Iterator[BaseNode]:
    yield from node.iterate_tree_level(level=level)


def iter_depth_first(node: BaseNode) -> Iterator[BaseNode]:
    yield node
    for child in iter_children(node):
        yield from iter_depth_first(child)
