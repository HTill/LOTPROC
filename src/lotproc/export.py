# pyright: reportMissingImports=false

from __future__ import annotations

from typing import Iterable

from numpy import ndarray

from lotdb import BaseNode


def _normalize_attribute_value(value):
    if isinstance(value, ndarray):
        return value.tolist()
    return value


def tree_to_dataframe(tree: BaseNode, attribute_list: list[str]):
    import pandas as pd

    leaves = list(tree.iterate_tree_leaves())
    rows: list[dict[str, object]] = []

    for node in leaves:
        path = list(node.gps())
        row: dict[str, object] = {}
        for idx, value in enumerate(path, start=1):
            row[f"TreeLevel_{idx}"] = value

        for attribute in attribute_list:
            row[attribute] = _normalize_attribute_value(node.ga(attribute))

        rows.append(row)

    return pd.DataFrame(rows)


def node_list_to_dataframe(node_list: Iterable[BaseNode], attribute_list: list[str]):
    import pandas as pd

    rows: list[dict[str, object]] = []

    for node in node_list:
        path = list(node.gps())
        row: dict[str, object] = {}
        for idx, value in enumerate(path, start=1):
            row[f"TreeLevel_{idx}"] = value

        for attribute in attribute_list:
            row[attribute] = _normalize_attribute_value(node.ga(attribute))

        rows.append(row)

    return pd.DataFrame(rows)
