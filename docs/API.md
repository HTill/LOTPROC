# LOTPROC API

## Core concepts

LOTPROC is built around a buffered processing pipeline for `lotdb`-style trees.
It depends on `lotdb` and operates on `lotdb.BaseNode` objects.

Recommended flow:

`traverse -> filter -> buffer -> prepare -> process -> write`

## Main public objects

### `Pipeline`
- Build composable workflows around a root tree or iterable source.
- Multiprocessing is only allowed after `buffer(...)`.
- Traversal delegates to `lotdb` tree iterators.

### `NodeRecord`
- Serializable node snapshot used for processing.
- Stores path, key, copied attributes, and optional payload.

### `ProcessResult`
- Serializable processing result.
- Stores source path plus output payload and attributes to write.

### Targets
- `WriteTarget`: generic writer bound to a root tree plus a write policy
- `InlineTarget`: writes under the same source path plus a child path like `_proc/...`
- `MirrorTarget`: writes to another root using the same relative path
- `NewDatabaseTarget`: semantic alias for writing into a separate root/new DB

### Write policies
- `InlineWritePolicy`
- `MirrorWritePolicy`
- `FreshDatabaseWritePolicy`

### `node_process_cruncher(...)`
- Convenience wrapper that builds a buffered pipeline and runs a processor over batches.

### Processing specs/builders
- `SelectionSpec`
- `PreparationSpec`
- `ProcessingSpec`
- `build_selection_pipeline(...)`
- `build_node_process_pipeline(...)`
- `add_preparation_stage(...)`
- `add_processing_stage(...)`
- `add_write_stage(...)`

### `lotproc.ingest`
- `load_files_folder(...)`
- `load_files_directory(...)`
- `load_small_files_folder(...)`
- `load_small_files_directory(...)`

### `lotproc.export`
- `tree_to_dataframe(...)`
- `node_list_to_dataframe(...)`

### `lotproc.serialization`
- `save_to_file(...)`
- `load_from_file(...)`

## Design rules

- traversal and filtering should stay lazy
- buffering is the materialization boundary
- multiprocessing should operate on prepared records, not live database nodes
- writes should happen in the parent process via targets
