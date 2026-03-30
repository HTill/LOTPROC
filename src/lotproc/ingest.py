# pyright: reportMissingImports=false

from __future__ import annotations

import os
from typing import Optional

from lotdb import BaseNode, DataWriter


def _resolve_parameter_separator(parameter_separator: Optional[str], parameter_seperator: Optional[str]) -> Optional[str]:
    if parameter_separator is None and parameter_seperator is not None:
        return parameter_seperator
    return parameter_separator


def load_files_directory(
    tree: BaseNode,
    dir_path: str,
    parameter_separator: Optional[str] = None,
    parameter_seperator: Optional[str] = None,
    filepath_attribute: str = "_pfo_audio_wav",
    file_extension: str = "wav",
) -> int:
    separator = _resolve_parameter_separator(parameter_separator, parameter_seperator)
    root_folder = os.path.basename(os.path.normpath(dir_path))
    parent_dir = os.path.dirname(os.path.normpath(dir_path))
    processed = 0

    for root, _, files in os.walk(dir_path):
        for file_name in files:
            if not file_name.endswith(f".{file_extension}"):
                continue

            relative_root = os.path.relpath(root, start=parent_dir)
            path_parts = relative_root.split(os.path.sep) if relative_root != "." else [root_folder]
            last_node = tree.gns(path_parts)

            stem = os.path.splitext(file_name)[0]
            cur_node = last_node.gn(stem) if separator is None else last_node.gns(stem.split(separator))
            DataWriter.attach_file_reference(cur_node, filepath_attribute=filepath_attribute, root=root, file=file_name)
            processed += 1

    return processed


def load_files_folder(
    tree: BaseNode,
    folder_path: str,
    parameter_separator: Optional[str] = "_~_",
    parameter_seperator: Optional[str] = None,
    filepath_attribute: str = "_pfo_audio_wav",
    file_extension: str = "wav",
) -> int:
    separator = _resolve_parameter_separator(parameter_separator, parameter_seperator)
    processed = 0

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(f".{file_extension}"):
            continue

        stem = os.path.splitext(file_name)[0]
        file_node_names = [stem] if separator is None else stem.split(separator)
        cur_node = tree.gns(file_node_names)
        DataWriter.attach_file_reference(cur_node, filepath_attribute=filepath_attribute, root=folder_path, file=file_name)
        processed += 1

    return processed


def load_small_files_directory(
    tree: BaseNode,
    dir_path: str,
    parameter_separator: Optional[str] = None,
    parameter_seperator: Optional[str] = None,
    filepath_attribute: str = "_pfo_audio_wav",
    file_extension: str = "wav",
) -> int:
    return load_files_directory(
        tree=tree,
        dir_path=dir_path,
        parameter_separator=parameter_separator,
        parameter_seperator=parameter_seperator,
        filepath_attribute=filepath_attribute,
        file_extension=file_extension,
    )


def load_small_files_folder(
    tree: BaseNode,
    folder_path: str,
    parameter_separator: Optional[str] = "_~_",
    parameter_seperator: Optional[str] = None,
    filepath_attribute: str = "_pfo_audio_wav",
    file_extension: str = "wav",
) -> int:
    return load_files_folder(
        tree=tree,
        folder_path=folder_path,
        parameter_separator=parameter_separator,
        parameter_seperator=parameter_seperator,
        filepath_attribute=filepath_attribute,
        file_extension=file_extension,
    )
