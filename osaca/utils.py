#!/usr/bin/env python3
import os.path

DATA_DIRS = [os.path.expanduser("~/.osaca/data"), os.path.join(os.path.dirname(__file__), "data")]
CACHE_DIR = os.path.expanduser("~/.osaca/cache")


def find_datafile(name):
    """Check for existence of name in user or package data folders and return path."""
    for dir in DATA_DIRS:
        path = os.path.join(dir, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find {!r} in {!r}.".format(name, DATA_DIRS))
