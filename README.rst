OSACA
=====

Open Source Architecture Code Analyzer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool allows automatic instruction fetching of assembly code,
auto-generating of testcases for assembly instructions creating latency
and throughput benchmarks on a specific instruction form and thorughput
analysis and throughput prediction for a inner-most loop code snippet.

.. image:: https://landscape.io/github/RRZE-HPC/OSACA/master/landscape.svg?style=flat&badge_auth_token=c95f01b247f94bc79c09d21c5c827697
   :target: https://landscape.io/github/RRZE-HPC/OSACA/master
   :alt: Code Health

Getting started
===============

Installation
~~~~~~~~~~~~
On most systems with python pip and setuputils installed, just run:
::
   pip install --user osaca
for the latest release.
If you want to build from source, clone this repository using ``git clone https://github.com/RRZE-HPC/OSACA`` and run in the root directory:
::
   python ./setup.py install

*Dependencies:*
~~~~~~~~~~~~~~~
Additional requirements are:

-  `Python <https://www.python.org/>`__ 3.5.2 or higher
-  `pandas <http://pandas.pydata.org/>`__ 0.18.1 or higher
-  `NumPy <http://www.numpy.org/>`__ 1.11.1 or higher
-  `kerncraft <https://github.com/RRZE-HPC/kerncraft>`__ 0.4.11 or
   higher
   
Usage
=====
Yet to be written.

Credits
=======
Implementation: Jan Laukemann

License
=======
:doc:`AGPL-3.0 </LICENSE>`
