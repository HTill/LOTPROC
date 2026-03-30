# pyright: reportMissingImports=false

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from lotdb import BaseNode

from .pipeline import Pipeline
from .targets import WriteTarget


@dataclass(frozen=True)
class SelectionSpec:
    traversal: str = "leaves"
    level: Any = "deepest"
    filter_fn: Optional[Callable[[Any], bool]] = None
    filter_key_pattern: Optional[str] = None
    invert_filter: bool = False


@dataclass(frozen=True)
class PreparationSpec:
    buffer_size: int = 1000
    prepare_fn: Optional[Callable[[Any], Any]] = None
    attribute_names: Optional[Sequence[str]] = None
    include_all_attributes: bool = False


@dataclass(frozen=True)
class ProcessingSpec:
    mode: str = "sync"
    workers: Optional[int] = None


def build_selection_pipeline(root: BaseNode, spec: SelectionSpec | None = None) -> Pipeline:
    spec = spec or SelectionSpec()
    pipeline = Pipeline.from_root(root).traverse(spec.traversal, level=spec.level)

    if spec.filter_fn is not None:
        pipeline = pipeline.filter(spec.filter_fn)

    if spec.filter_key_pattern is not None:
        pipeline = pipeline.filter_key(spec.filter_key_pattern, invert=spec.invert_filter)

    return pipeline


def add_preparation_stage(pipeline: Pipeline, spec: PreparationSpec | None = None) -> Pipeline:
    spec = spec or PreparationSpec()
    return pipeline.buffer(spec.buffer_size).prepare(
        spec.prepare_fn,
        attribute_names=spec.attribute_names,
        include_all_attributes=spec.include_all_attributes,
    )


def add_processing_stage(
    pipeline: Pipeline,
    processor: Callable[[Any], Any],
    spec: ProcessingSpec | None = None,
) -> Pipeline:
    spec = spec or ProcessingSpec()
    return pipeline.process(processor, mode=spec.mode, workers=spec.workers)


def add_write_stage(pipeline: Pipeline, target: WriteTarget | None = None) -> Pipeline:
    if target is not None:
        return pipeline.write(target)
    return pipeline


def build_node_process_pipeline(
    root: BaseNode,
    processor: Callable[[Any], Any],
    *,
    selection: SelectionSpec | None = None,
    preparation: PreparationSpec | None = None,
    processing: ProcessingSpec | None = None,
    target: Optional[WriteTarget] = None,
) -> Pipeline:
    pipeline = build_selection_pipeline(root, selection)
    pipeline = add_preparation_stage(pipeline, preparation)
    pipeline = add_processing_stage(pipeline, processor, processing)
    return add_write_stage(pipeline, target)


def node_process_cruncher(
    root: BaseNode,
    processor: Callable[[Any], Any],
    *,
    traversal: str = "leaves",
    level: Any = "deepest",
    filter_fn: Optional[Callable[[Any], bool]] = None,
    filter_key_pattern: Optional[str] = None,
    invert_filter: bool = False,
    buffer_size: int = 1000,
    prepare_fn: Optional[Callable[[Any], Any]] = None,
    attribute_names: Optional[Sequence[str]] = None,
    include_all_attributes: bool = False,
    mode: str = "sync",
    workers: Optional[int] = None,
    target: Optional[WriteTarget] = None,
):
    return build_node_process_pipeline(
        root,
        processor,
        selection=SelectionSpec(
            traversal=traversal,
            level=level,
            filter_fn=filter_fn,
            filter_key_pattern=filter_key_pattern,
            invert_filter=invert_filter,
        ),
        preparation=PreparationSpec(
            buffer_size=buffer_size,
            prepare_fn=prepare_fn,
            attribute_names=attribute_names,
            include_all_attributes=include_all_attributes,
        ),
        processing=ProcessingSpec(mode=mode, workers=workers),
        target=target,
    ).run()
