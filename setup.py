#!/usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.sdist import sdist as _sdist

# To use a consistent encoding
from codecs import open
import os
import io
import re
import sys

here = os.path.abspath(os.path.dirname(__file__))


# Stolen from pip
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


# Stolen from pip
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def _run_build_cache(dir):
    from subprocess import check_call

    # This is run inside the install staging directory (that had no .pyc files)
    # We don't want to generate any.
    # https://github.com/eliben/pycparser/pull/135
    check_call([sys.executable, "-B", "_build_cache.py"], cwd=os.path.join(dir, "osaca", "data"))


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_run_build_cache, (self.install_lib,), msg="Build ISA and architecture cache")


class sdist(_sdist):
    def make_release_tree(self, basedir, files):
        _sdist.make_release_tree(self, basedir, files)
        self.execute(_run_build_cache, (basedir,), msg="Build ISA and architecture cache")


# Get the long description from the README file
with open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="osaca",
    # Version should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    #  https://packaging.python.org/en/latest/distributing.html
    version=find_version("osaca", "__init__.py"),
    description="Open Source Architecture Code Analyzer",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # The project's main homepage
    url="https://github.com/RRZE-HPC/OSACA",
    # Author details
    author="Jan Laukemann",
    author_email="jan.laukemann@fau.de",
    # Choose your license
    license="AGPLv3",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Utilities",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: GNU Affero General Public License v3",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate wheter you support Python2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    # What doesd your project relate to?
    keywords="hpc performance benchmark analysis architecture",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=["networkx", "pyparsing>=2.3.1", "ruamel.yaml>=0.15.71"],
    python_requires=">=3.5",
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    # },
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={"console_scripts": ["osaca=osaca.osaca:main"]},
    # Overwriting install and sdist to enforce cache distribution with package
    cmdclass={"install": install, "sdist": sdist},
)
