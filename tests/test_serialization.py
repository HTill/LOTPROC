# pyright: reportMissingImports=false

from lotproc import load_from_file, save_to_file


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "sample"
    payload = {"a": 1, "b": [1, 2, 3]}

    save_to_file(payload, path)
    loaded = load_from_file(tmp_path / "sample.pyobj")

    assert loaded == payload
