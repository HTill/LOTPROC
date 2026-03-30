# pyright: reportMissingImports=false

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any, Callable, Optional

from lotdb import BaseNode


def filter_nodes(nodes: Iterable[BaseNode], predicate: Callable[[BaseNode], bool]) -> Iterator[BaseNode]:
    for node in nodes:
        if predicate(node):
            yield node


def filter_node_list(filter_str: str, node_list: list[BaseNode], invers: bool = False) -> list[BaseNode]:
    return list(filter_key_regex(node_list, filter_str, invert=invers))


def filter_key_regex(nodes: Iterable[BaseNode], pattern: str, *, invert: bool = False) -> Iterator[BaseNode]:
    regex = re.compile(pattern)
    for node in nodes:
        matches = regex.search(node.key) is not None
        if matches != invert:
            yield node


def filter_attribute(
    nodes: Iterable[BaseNode],
    name: str,
    *,
    equals: Any = None,
    predicate: Optional[Callable[[Any], bool]] = None,
    invert: bool = False,
) -> Iterator[BaseNode]:
    if predicate is None:
        predicate = lambda value: value == equals

    for node in nodes:
        value = node.get_attribute(name, None)

        matches = predicate(value)
        if matches != invert:
            yield node
