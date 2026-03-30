# pyright: reportMissingImports=false

from __future__ import annotations

from lotdb import BaseNode


def test_counter(node: BaseNode, offset: int):
    node.ga("c", node.ga("a") + node.ga("b") + offset)
    return node
