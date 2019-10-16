#!/usr/bin/env python3
import os.path


def find_file(name):
    """Check for existence of name in user or package data folders and return path."""
    search_paths = [os.path.expanduser('~/.osaca/data'),
                    os.path.join(os.path.dirname(__file__), 'data')]
    for dir in search_paths:
        path = os.path.join(dir, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find {!r} in {!r}.".format(name, search_paths))