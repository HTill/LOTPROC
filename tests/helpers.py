# pyright: reportMissingImports=false

from __future__ import annotations

from lotdb import BaseNode

from lotproc import ProcessResult


def build_sample_tree() -> BaseNode:
    root = BaseNode("root")
    root.gns(["speaker_01", "session_a", "clip_001"]).set_attribute("duration", 1.2)
    root.gns(["speaker_01", "session_a", "clip_002"]).set_attribute("duration", 1.4)
    root.gns(["speaker_02", "session_b", "clip_003"]).set_attribute("duration", 0.8)
    return root


def summarize_batch(records):
    return [
        ProcessResult(
            path=record.path,
            output={
                "path": record.path,
                "duration": record.attributes.get("duration"),
            },
            attributes={"processed": True},
        )
        for record in records
    ]


def uppercase_batch_keys(records):
    return [
        ProcessResult(
            path=record.path,
            output=record.key.upper(),
            relative_path=("derived",),
            attributes={"source_duration": record.attributes.get("duration")},
        )
        for record in records
    ]
