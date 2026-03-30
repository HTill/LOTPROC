# pyright: reportMissingImports=false

from lotproc import (
    InlineTarget,
    PreparationSpec,
    ProcessingSpec,
    SelectionSpec,
    build_node_process_pipeline,
    node_process_cruncher,
)

from .helpers import build_sample_tree, summarize_batch


def test_node_process_cruncher_runs_buffered_pipeline_and_writes_results():
    root = build_sample_tree()
    target = InlineTarget(root=root, base_path=("_proc", "crunch"))

    returned_target = node_process_cruncher(
        root,
        summarize_batch,
        filter_key_pattern=r"clip_00[12]",
        buffer_size=2,
        attribute_names=["duration"],
        target=target,
    )

    assert returned_target is target
    assert root.gns(["speaker_01", "session_a", "clip_001", "_proc", "crunch"]).get_attribute("processed") is True


def test_build_node_process_pipeline_exposes_reusable_stages():
    root = build_sample_tree()
    target = InlineTarget(root=root, base_path=("_proc", "spec"))

    pipeline = build_node_process_pipeline(
        root,
        summarize_batch,
        selection=SelectionSpec(filter_key_pattern=r"clip_001"),
        preparation=PreparationSpec(buffer_size=1, attribute_names=["duration"]),
        processing=ProcessingSpec(),
        target=target,
    )

    returned_target = pipeline.run()

    assert returned_target is target
    assert root.gns(["speaker_01", "session_a", "clip_001", "_proc", "spec"]).get_attribute("processed") is True
