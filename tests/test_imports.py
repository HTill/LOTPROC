# pyright: reportMissingImports=false

import lotproc


def test_package_imports():
    assert lotproc is not None
    assert hasattr(lotproc, "Pipeline")
    assert hasattr(lotproc, "node_process_cruncher")
    assert hasattr(lotproc, "WriteTarget")
    assert hasattr(lotproc, "InlineWritePolicy")
    assert hasattr(lotproc, "load_files_folder")
    assert hasattr(lotproc, "tree_to_dataframe")
