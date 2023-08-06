import os
import shutil
import secrets
import string
from typing import NewType

NewPath = NewType('NewPath', str)

DEFAULT_PASSES = 2


def _overwrite_file(file_path: str, passes: int, zeros=False):
    """overwrite a single file with secure random data passes times
    uses secrets library or zeros is zeros is set to true"""
    file_size: int = os.path.getsize(file_path)

    for _ in range(passes):
        if zeros:
            new_data = b'0' * file_size
        else:
            new_data = secrets.token_bytes(file_size)

        with open(file_path, 'wb') as top_secret_file:
            top_secret_file.write(new_data)


def _rename_inode(path_in: str, zeros=False) -> NewPath:
    """renames file randomly, or with zeros if zeros is true"""
    name_len = len(os.path.basename(path_in))
    new_name = ''
    path = os.path.abspath(path_in)
    dir_n = os.path.dirname(path_in)
    if dir_n:
        dir_n += '/'

    if zeros:
        new_name = '0' * name_len
    else:
        for _ in range(name_len):
            new_name += secrets.choice(string.ascii_letters)

    os.rename(path, dir_n + new_name)

    return dir_n + new_name


def _nuke(path: str, passes: int = DEFAULT_PASSES):
    """properly delete inode"""
    if os.path.isfile(path):
        _overwrite_file(path, passes)
        new_path = _rename_inode(path)
        os.remove(new_path)
    else:
        new_path = _rename_inode(path)
        shutil.rmtree(new_path)


def clean_tree(directory: str, passes: int = DEFAULT_PASSES):
    """securely delete dir tree"""
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            _nuke(os.path.join(root, name))
        for name in dirs:
            _nuke(os.path.join(root, name))
    _nuke(directory)


def clean(path: str):
    """securely delete path"""
    _nuke(path)
