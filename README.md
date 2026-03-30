# LOTPROC

Light Object Tree processing toolkit.

LOTPROC is intended as a lightweight processing layer for `lotdb` workflows.
It depends on `lotdb` and is designed around real `lotdb.BaseNode` trees.

The main idea is to replace hand-written nested `for` loops with composable pipeline blocks:

- traverse
- filter
- buffer
- prepare
- process
- write

This repository mirrors the same high-level layout as `lotdb`:

- `src/lotproc` for the installable package
- `tests/` for test coverage
- `docs/` for API and design notes
- `.github/workflows/` for CI and publishing automation

## Current building blocks

- `lotproc.traversal`: leaf and level traversal helpers
- `lotproc.filters`: regex and attribute-based filters
- `lotproc.buffering`: buffered materialization of lazy iterators
- `lotproc.pipeline.Pipeline`: composable workflow API
- `lotproc.processors.node_process_cruncher`: high-level buffered processing helper
- `lotproc.targets`: inline, mirrored, and new-database write targets
- `lotproc.write_policies`: reusable path policies for inline, mirrored, and fresh-db writes
- `lotproc.ingest`: file-to-tree indexing helpers moved out of `lotdb`
- `lotproc.export`: dataframe export helpers moved out of `lotdb`
- `lotproc.serialization`: simple object persistence helpers

The processing layer is also available as reusable specs/stages rather than one single cruncher helper:

- `SelectionSpec`
- `PreparationSpec`
- `ProcessingSpec`
- `build_node_process_pipeline(...)`

So `node_process_cruncher(...)` is now just the convenience wrapper on top.

## Example

```python
from lotdb import LOTDB
from lotproc import InlineTarget, Pipeline, ProcessResult


def summarize_batch(records):
    return [
        ProcessResult(
            path=record.path,
            output={"duration": record.attributes.get("duration")},
            attributes={"processed": True},
        )
        for record in records
    ]


db = LOTDB(path="./data", name="lotdb.fs", new=True)
root = db.open_connection()

root.gns(["speaker_01", "session_a", "clip_001"]).set_attribute("duration", 1.2)
root.gns(["speaker_01", "session_a", "clip_002"]).set_attribute("duration", 1.4)

Pipeline.from_root(root) \
    .traverse("leaves") \
    .filter_key(r"clip_.*") \
    .buffer(128) \
    .prepare(attribute_names=["duration"]) \
    .process(summarize_batch) \
    .write(InlineTarget(root=root, base_path=("_proc", "summary"))) \
    .run()

db.commit()
db.close_connection()
db.close()
```

## What `prepare(...)` does

`prepare(...)` converts live `lotdb.BaseNode` objects into serializable `NodeRecord` snapshots.

That means your processor receives records with things like:

- `path`
- `key`
- selected `attributes`
- optional `payload`

Example:

```python
.prepare(attribute_names=["duration"])
```

After that, the processor gets batches like:

```python
[
    NodeRecord(
        path=("speaker_01", "session_a", "clip_001"),
        key="clip_001",
        attributes={"duration": 1.2},
    )
]
```

Why this matters:

- processing code becomes independent from live DB nodes
- multiprocessing becomes safer
- workers operate on materialized data, not persistent objects

## Write targets and policies

- `InlineTarget(...)`: write under the same source tree
- `MirrorTarget(...)`: write into another tree with mirrored paths
- `NewDatabaseTarget(...)`: write into a fresh/separate tree or DB
- `WriteTarget(..., policy=...)`: fully explicit target + write-policy combination

Example:

```python
from lotproc import InlineWritePolicy, WriteTarget

target = WriteTarget(
    root=root,
    policy=InlineWritePolicy(base_path=("results", "run_001")),
    output_attribute="result",
)
```

## Reusable processing specs

```python
from lotproc import (
    InlineTarget,
    PreparationSpec,
    ProcessingSpec,
    SelectionSpec,
    build_node_process_pipeline,
)


pipeline = build_node_process_pipeline(
    root,
    summarize_batch,
    selection=SelectionSpec(filter_key_pattern=r"clip_001"),
    preparation=PreparationSpec(buffer_size=32, attribute_names=["duration"]),
    processing=ProcessingSpec(mode="sync"),
    target=InlineTarget(root=root, base_path=("_proc", "spec")),
)

pipeline.run()
```

Multiprocessing is intentionally gated behind buffering so that worker processes receive materialized, serializable batches instead of live database node objects.

The underlying tree iteration primitives remain in `lotdb`; LOTPROC wraps and composes them into processing workflows.

## Development

Editable install:

`pip install -e .[dev]`

Run tests:

`pytest`
