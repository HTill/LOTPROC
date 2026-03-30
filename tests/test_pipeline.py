# pyright: reportMissingImports=false

from lotproc import (
    InlineTarget,
    InlineWritePolicy,
    MirrorTarget,
    NewDatabaseTarget,
    Pipeline,
    ProcessResult,
    WriteTarget,
    filter_node_list,
)

from .helpers import build_sample_tree, summarize_batch, uppercase_batch_keys


def test_filter_node_list_matches_regex_on_keys():
    root = build_sample_tree()
    leaves = list(root.gns(["speaker_01", "session_a"]).all_nodes()) + [root.gns(["speaker_02", "session_b", "clip_003"])]

    filtered = filter_node_list(r"clip_00[12]", leaves)

    assert [node.key for node in filtered] == ["clip_001", "clip_002"]


def test_pipeline_buffers_and_writes_inline_results():
    root = build_sample_tree()

    target = (
        Pipeline.from_root(root)
        .traverse("leaves")
        .filter_key(r"clip_00[12]")
        .buffer(2)
        .prepare(attribute_names=["duration"])
        .process(summarize_batch)
        .write(InlineTarget(root=root, base_path=("_proc", "summary")))
        .run()
    )

    assert target.written_paths == [
        ("speaker_01", "session_a", "clip_001", "_proc", "summary"),
        ("speaker_01", "session_a", "clip_002", "_proc", "summary"),
    ]
    assert root.gns(["speaker_01", "session_a", "clip_001", "_proc", "summary"]).get_attribute("processed") is True


def test_pipeline_supports_explicit_write_policy_target():
    root = build_sample_tree()

    target = (
        Pipeline.from_root(root)
        .traverse("leaves")
        .filter_key(r"clip_001")
        .buffer(1)
        .prepare(attribute_names=["duration"])
        .process(summarize_batch)
        .write(WriteTarget(root=root, policy=InlineWritePolicy(base_path=("results",))))
        .run()
    )

    assert target.written_paths == [("speaker_01", "session_a", "clip_001", "results")]
    assert root.gns(["speaker_01", "session_a", "clip_001", "results"]).get_attribute("processed") is True


def test_pipeline_requires_buffer_before_multiprocessing():
    root = build_sample_tree()

    try:
        Pipeline.from_root(root).traverse("leaves").prepare(attribute_names=["duration"]).process(
            summarize_batch,
            mode="process",
        )
    except ValueError as exc:
        assert "Multiprocessing requires buffered batches" in str(exc)
    else:
        raise AssertionError("Expected process mode without buffering to fail.")


def test_pipeline_can_process_to_mirror_target_with_multiprocessing():
    root = build_sample_tree()
    mirror = build_sample_tree()

    target = (
        Pipeline.from_root(root)
        .traverse("leaves")
        .buffer(2)
        .prepare(attribute_names=["duration"])
        .process(uppercase_batch_keys, mode="process", workers=2)
        .write(MirrorTarget(root=mirror, output_attribute="value"))
        .run()
    )

    assert len(target.written_paths) == 3
    assert mirror.gns(["speaker_01", "session_a", "clip_001", "derived"]).get_attribute("value") == "CLIP_001"


def test_new_database_target_writes_to_separate_tree():
    root = build_sample_tree()
    new_root = build_sample_tree()

    results = [
        ProcessResult(
            path=("speaker_02", "session_b", "clip_003"),
            output={"score": 0.91},
            attributes={"status": "done"},
        )
    ]

    target = NewDatabaseTarget(root=new_root, output_attribute="payload")
    target.write_many(results)

    written = new_root.gns(["speaker_02", "session_b", "clip_003"])
    assert written.get_attribute("payload") == {"score": 0.91}
    assert written.get_attribute("status") == "done"
