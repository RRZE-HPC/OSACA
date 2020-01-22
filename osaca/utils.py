#!/usr/bin/env python3
import os.path

CACHE_DIR = os.path.expanduser('~/.osaca/cache')


def find_file(name):
    """Check for existence of name in user or package data folders and return path."""
    search_paths = [os.path.expanduser('~/.osaca/data'),
                    os.path.join(os.path.dirname(__file__), 'data')]
    for dir in search_paths:
        path = os.path.join(dir, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find {!r} in {!r}.".format(name, search_paths))


def exists_cached_file(name):
    """Check for existence of file in cache dir. Returns path if it exists and False otherwise."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        return False
    search_paths = [CACHE_DIR]
    for dir in search_paths:
        path = os.path.join(dir, name)
        if os.path.exists(path):
            return path
    return False
