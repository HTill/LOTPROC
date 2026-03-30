from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import get_context
from typing import Any, Optional


def _call_processor(args: tuple[Callable[[Any], Any], Any]) -> Any:
    fn, batch = args
    return fn(batch)


def process_batches(
    batches: Iterable[Any],
    processor: Callable[[Any], Any],
    *,
    mode: str = "sync",
    workers: Optional[int] = None,
) -> Iterator[Any]:
    if mode == "sync":
        for batch in batches:
            yield processor(batch)
        return

    if mode == "thread":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for result in executor.map(processor, batches):
                yield result
        return

    if mode == "process":
        batch_list = list(batches)
        with get_context("spawn").Pool(processes=workers) as pool:
            for result in pool.map(_call_processor, [(processor, batch) for batch in batch_list]):
                yield result
        return

    raise ValueError("mode must be one of: 'sync', 'thread', 'process'.")
