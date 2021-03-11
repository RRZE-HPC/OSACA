import io
import os
import re


# Stolen from pip
def __read(*names, **kwargs):
    """Reads in file"""
    with io.open(
        os.path.join(os.path.dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


# Stolen from pip
def __find_version(*file_paths):
    """Searches for a version attribute in the given file(s)"""
    version_file = __read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_version():
    """
    Gets the current OSACA version stated in the __init__ file

    :returns: str -- the version string.
    """
    return __find_version("../osaca/__init__.py")
