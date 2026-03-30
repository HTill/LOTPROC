# pyright: reportMissingImports=false

from pathlib import Path

from lotdb import LOTDB
from lotproc import load_files_directory, load_files_folder


def test_load_files_folder_builds_tree(tmp_path):
    data_dir = tmp_path / "audio"
    data_dir.mkdir()
    (data_dir / "speaker1_~_utt1.wav").write_bytes(b"")
    (data_dir / "speaker1_~_utt2.wav").write_bytes(b"")

    db = LOTDB(path=str(tmp_path), name="folder.fs", new=True)
    tree = db.open_connection()
    processed = load_files_folder(tree, str(data_dir))
    db.commit()

    assert processed == 2

    node = tree.gns(["speaker1", "utt1"])
    assert Path(node.ga("_pfo_audio_wav").filepath).name == "speaker1_~_utt1.wav"

    db.close_connection()
    db.close()


def test_load_files_directory_builds_tree_from_nested_folders(tmp_path):
    nested = tmp_path / "dataset" / "speaker1"
    nested.mkdir(parents=True)
    (nested / "utt1.wav").write_bytes(b"")

    db = LOTDB(path=str(tmp_path), name="dir.fs", new=True)
    tree = db.open_connection()
    processed = load_files_directory(tree, str(tmp_path / "dataset"))
    db.commit()

    assert processed == 1
    assert tree.gns(["dataset", "speaker1", "utt1"]).ga("_pfo_audio_wav") is not None

    db.close_connection()
    db.close()
