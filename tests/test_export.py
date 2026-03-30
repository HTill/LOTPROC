# pyright: reportMissingImports=false

import pandas as pd

from lotproc import node_list_to_dataframe, tree_to_dataframe

from .helpers import build_sample_tree


def test_tree_to_dataframe_exports_leaf_rows():
    root = build_sample_tree()
    frame = tree_to_dataframe(root, ["duration"])

    assert isinstance(frame, pd.DataFrame)
    assert set(frame["TreeLevel_1"].tolist()) == {"speaker_01", "speaker_02"}
    assert "duration" in frame.columns
    assert len(frame) == 3


def test_node_list_to_dataframe_exports_selected_nodes():
    root = build_sample_tree()
    nodes = [root.gns(["speaker_01", "session_a", "clip_001"]), root.gns(["speaker_02", "session_b", "clip_003"])]

    frame = node_list_to_dataframe(nodes, ["duration"])

    assert frame["TreeLevel_3"].tolist() == ["clip_001", "clip_003"]
    assert frame["duration"].tolist() == [1.2, 0.8]
