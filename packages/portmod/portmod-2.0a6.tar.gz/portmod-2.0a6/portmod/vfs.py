# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Functions for interacting with the OpenMW VFS
"""

import os
from .config import get_config
from .util import ci_exists
from .configfile import read_config, find_config


def find_file(name: str) -> str:
    """
    Locates the path of a file within the OpenMW virtual file system
    """
    configpath = os.path.expanduser(get_config()["OPENMW_CONFIG"])
    config = read_config(configpath)

    for index, directory in find_config(config, "data=*")[::-1]:
        directory = directory.replace("data=", "").lstrip('"').rstrip('"')
        path = ci_exists(os.path.join(directory, name))
        if path:
            return path

    raise FileNotFoundError(name)


def list_dir(name: str) -> str:
    """
    Locates all path of files matching the given pattern within the OpenMW
    virtual file system
    """
    configpath = os.path.expanduser(get_config()["OPENMW_CONFIG"])
    config = read_config(configpath)

    files = {}

    for index, directory in find_config(config, "data=*")[::-1]:
        directory = directory.replace("data=", "").lstrip('"').rstrip('"')
        path = ci_exists(os.path.join(directory, name))
        if path:
            for file in os.listdir(path):
                if file.lower() not in files:
                    files[file.lower()] = os.path.join(path, file)

    return sorted(files.values())
