# LOTPROC

Light Object Tree processing toolkit built on top of `lotdb`.

LOTPROC is the processing/workflow layer for LOTDB trees:

- traverse
- filter
- buffer
- prepare
- process
- write

## Install

```bash
pip install lotdb lotproc
```

## Basic idea

`lotdb` owns storage and tree mechanics.
`lotproc` owns filtering, batching, processing, and write strategies.

## Example: buffered processing pipeline

```python
from lotdb import LOTDB
from lotproc import Pipeline, InlineTarget, ProcessResult

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

## Example: mirrored output tree

```python
from lotdb import BaseNode
from lotproc import MirrorTarget, Pipeline, ProcessResult

def uppercase_keys(records):
    return [
        ProcessResult(
            path=record.path,
            output=record.key.upper(),
            relative_path=("derived",),
        )
        for record in records
    ]

source_root = BaseNode("root")
source_root.gns(["speaker_01", "session_a", "clip_001"])

mirror_root = BaseNode("mirror")

Pipeline.from_root(source_root) \
    .traverse("leaves") \
    .buffer(64) \
    .prepare() \
    .process(uppercase_keys, mode="sync") \
    .write(MirrorTarget(root=mirror_root, output_attribute="value")) \
    .run()
```

## Example: explicit write policy

```python
from lotproc import InlineWritePolicy, WriteTarget

target = WriteTarget(
    root=root,
    policy=InlineWritePolicy(base_path=("results", "run_001")),
    output_attribute="result",
)
```

## Example: reusable processing specs

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

## Multiprocessing note

Multiprocessing is only allowed after buffering.
That way workers receive materialized, serializable batches instead of live LOTDB nodes.

## Status

The full source is currently prepared locally and can be pushed into this repository next.
