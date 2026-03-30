from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


def buffer_iterable(items: Iterable[T], buffer_size: int) -> Iterator[list[T]]:
    if buffer_size <= 0:
        raise ValueError("buffer_size must be greater than 0.")

    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == buffer_size:
            yield batch
            batch = []

    if batch:
        yield batch
