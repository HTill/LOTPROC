# pyright: reportMissingImports=false

from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence

from lotdb import BaseNode

from .models import NodeRecord


def node_path(node: BaseNode) -> tuple[str, ...]:
    return tuple(node.gps())


def node_attributes(
    node: BaseNode,
    attribute_names: Optional[Sequence[str]] = None,
    *,
    include_all: bool = False,
) -> dict[str, Any]:
    if attribute_names is None and not include_all:
        return {}

    if include_all:
        attribute_names = list(node.all_attribute_keys())

    values: dict[str, Any] = {}
    for name in attribute_names or ():
        values[str(name)] = node.get_attribute(name)

    return values


def node_to_record(
    node: BaseNode,
    *,
    attribute_names: Optional[Sequence[str]] = None,
    include_all_attributes: bool = False,
    payload: Any = None,
) -> NodeRecord:
    return NodeRecord(
        path=node_path(node),
        key=node.key,
        attributes=node_attributes(node, attribute_names, include_all=include_all_attributes),
        payload=payload,
    )


def nodes_to_records(
    nodes: Iterable[BaseNode],
    *,
    attribute_names: Optional[Sequence[str]] = None,
    include_all_attributes: bool = False,
) -> list[NodeRecord]:
    return [
        node_to_record(
            node,
            attribute_names=attribute_names,
            include_all_attributes=include_all_attributes,
        )
        for node in nodes
    ]
