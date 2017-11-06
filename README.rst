OSACA
=====

Open Source Architecture Code Analyzer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool allows automatic instruction fetching of assembly code,
auto-generating of testcases for assembly instructions creating latency
and throughput benchmarks on a specific instruction form and throughput
analysis and throughput prediction for a innermost loop kernel.

.. image:: https://travis-ci.com/RRZE-HPC/OSACA.svg?token=393L6z2HEXNiGLtZ43s6&branch=master
    :target: https://travis-ci.com/RRZE-HPC/OSACA

.. image:: https://landscape.io/github/RRZE-HPC/OSACA/master/landscape.svg?style=flat&badge_auth_token=c95f01b247f94bc79c09d21c5c827697
   :target: https://landscape.io/github/RRZE-HPC/OSACA/master
   :alt: Code Health

Getting started
===============

Installation
~~~~~~~~~~~~
.. On most systems with python pip and setuputils installed, just run:
.. ::
   pip install --user osaca
.. for the latest release.
To build OSACA from source, clone this repository using ``git clone https://github.com/RRZE-HPC/OSACA`` and run in the root directory:
::
   python ./setup.py install

After installation, OSACA can be started with the command ``osaca`` in the CLI.

Dependencies:
~~~~~~~~~~~~~~~
Additional requirements are:

-  `Python3 <https://www.python.org/>`_
-  `pandas <http://pandas.pydata.org/>`_
-  `NumPy <http://www.numpy.org/>`_
-  `Kerncraft <https://github.com/RRZE-HPC/kerncraft>`_
-   `ibench <https://github.com/hofm/ibench`_    for throughput/latency measurements
   
Usage
=====

The usage of OSACA can be listed as:
::
    osaca [-h] [-V] [--arch ARCH] [--tp-list] [-i | --iaca | -m] FILEPATH

- ``-h`` or ``--help`` prints out the help message.
- ``-V`` or ``--version`` shows the program’s version number.
- ``ARCH`` needs to be replaced with the wished architecture abbreviation. This flag is necessary for the throughput analysis (default function) and the inclusion of an ibench output (``-i``). Possible options are ``SNB``, ``IVB``, ``HSW``, ``BDW`` and ``SKL`` for the latest Intel micro architectures starting from Intel Sandy Bridge.
- While in the throughput analysis mode, one can add ``--tp-list`` for printing the additional throughput list of the kernel or ``--iaca`` for letting OSACA to know it has to search for IACA binary markers.
- ``-i`` or ``--include-ibench`` starts the integration of ibench output into the CSV data file determined by ``ARCH``.
- With the flag ``-m`` or ``--insert-marker`` OSACA calls the Kerncraft module for the interactively insertion of `IACA <https://software.intel.com/en-us/articles/intel-architecture-code-analyzer>`_ marker in suggested assembly blocks.
- ``FILEPATH`` describes the filepath to the file to work with and is always necessary

Hereinafter the main tasks will be described.

Throughput analysis
~~~~~~~~~~~~~~~~~~~
Lorem ipsum

Include new measurements into the data file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lorem ipsum

Insert IACA markers
~~~~~~~~~~~~~~~~~~~
Lorem ipsum


Credits
=======
Implementation: Jan Laukemann

License
=======
`AGPL-3.0 </LICENSE>`_
