.. image:: doc/osaca-logo.png
   :alt: OSACA logo
   :width: 80%
   
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

.. ..image:: https://landscape.io/github/RRZE-HPC/OSACA/master/landscape.svg?style=flat&badge_auth_token=c95f01b247f94bc79c09d21c5c827697
..   :target: https://landscape.io/github/RRZE-HPC/OSACA/master
..   :alt: Code Health

.. image:: https://codecov.io/github/RRZE-HPC/OSACA/coverage.svg?branch=master
    :target: https://codecov.io/github/RRZE-HPC/OSACA?branch=master

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

Getting started
===============

Installation
~~~~~~~~~~~~
On most systems with python pip and setuputils installed, just run:

.. code:: bash

    pip install --user osaca

for the latest release.

To build OSACA from source, clone this repository using ``git clone https://github.com/RRZE-HPC/OSACA`` and run in the root directory:

.. code:: bash

   python ./setup.py install

After installation, OSACA can be started with the command ``osaca`` in the CLI.

Dependencies:
~~~~~~~~~~~~~~~
Additional requirements are:

-  `Python3 <https://www.python.org/>`_
-  `Graphviz <https://www.graphviz.org/>`_ for dependency graph creation (minimal dependency is `libgraphviz-dev` on Ubuntu)
-  `Kerncraft <https://github.com/RRZE-HPC/kerncraft>`_ for marker insertion
-   `ibench <https://github.com/hofm/ibench>`_ for throughput/latency measurements

Design
======
A schematic design of OSACA's workflow is shown below:

.. image:: doc/osaca-workflow.png
   :alt: OSACA workflow
   :width: 80%

Usage
=====

The usage of OSACA can be listed as:

.. code:: bash

    osaca [-h] [-V] [--arch ARCH] [--export-graph GRAPHNAME] FILEPATH

-h, --help
  prints out the help message.
-V, --version
  shows the program’s version number.
--arch ARCH
  needs to be replaced with the wished architecture abbreviation.
  This flag is necessary for the throughput analysis (default function) and the inclusion of an ibench output (``-i``).
  Possible options are ``SNB``, ``IVB``, ``HSW``, ``BDW``, ``SKX`` and ``CSX`` for the latest Intel micro architectures starting from Intel Sandy Bridge and ``ZEN1`` for AMD Zen (17h family) architecture.
  Furthermore, `VULCAN` for Marvell`s ARM-based ThunderX2 architecture is available.
--insert-marker
  OSACA calls the Kerncraft module for the interactively insertion of `IACA <https://software.intel.com/en-us/articles/intel-architecture-code-analyzer>`_ marker in suggested assembly blocks.
--db-check
  Run a sanity check on the by "--arch" specified database.
  The output depends on the verbosity level.
  Keep in mind you have to provide a (dummy) filename in anyway.
--export-graph EXPORT_PATH
  Output path for .dot file export. If "." is given, the file will be stored as "./osaca_dg.dot".
  After the file was created, you can convert it to a PDF file using dot: `dot -Tpdf osaca_dg.dot -o osaca_dependency_graph.pdf`

The **FILEPATH** describes the filepath to the file to work with and is always necessary

______________________

Hereinafter OSACA's scope of function will be described.

Throughput & Latency analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As main functionality of OSACA this process starts by default. It is always necessary to specify the core architecture by the flag ``--arch ARCH``, where ``ARCH`` can stand for ``SNB``, ``IVB``, ``HSW``, ``BDW``, ``SKX``, ``CSX``, ``ZEN`` or ``VULCAN``.

For extracting the right kernel, one has to mark it beforehand.
Currently, only the detechtion of markers in the assembly code and therefore the analysis of assemly files is supported by OSACA.

**Assembly code**

Marking a kernel means to insert the byte markers in the assembly file in before and after the loop.
For this, the start marker has to be inserted right in front of the loop label and the end marker directly after the jump instruction.
For the convience of the user, in x86 assembly IACA byte markers are used.

**x86 Byte Markers**

.. code-block:: gas

    movl    $111,%ebx       #IACA/OSACA START MARKER
    .byte   100,103,144     #IACA/OSACA START MARKER
    Loop:
      # ...
    movl    $222,%ebx       #IACA/OSACA END MARKER
    .byte   100,103,144     #IACA/OSACA END MARKER

**AArch64 Byte Markers**

.. code-block:: asm

    mov x1, #111            // OSACA START
    .byte 213,3,32,31       // OSACA START
      \\ ...
    mov x1, #222            // OSACA END
    .byte 213,3,32,31       // OSACA END

.. Include new measurements into the data file
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. Running OSACA with the flag ``-i`` or ``--include-ibench`` and a specified micro architecture ``ARCH``, it takes the values given in an ibench output file and checks them for reasonability. If a value is not in the data file already, it will be added, otherwise OSACA prints out a warning message and keeps the old value in the data file. If a value does not pass the validation, a warning message is shown, however, OSACA will keep working with the new value. The handling of ibench is shortly described in the example section below.

Insert IACA markers
~~~~~~~~~~~~~~~~~~~
Using the ``--insert-marker`` flags for a given file, OSACA calls the implemented Kerncraft module for identifying and marking the inner-loop block in *manual mode*. More information about how this is done can be found in the `Kerncraft repository <https://github.com/RRZE-HPC/kerncraft>`_.
Note that this currrently only works for x86 loop kernels

Example
=======
For clarifying the functionality of OSACA a sample kernel is analyzed for an Intel CSX core hereafter:

.. code-block:: c

    double a[N], double b[N];
    double s;
    
    // loop
    for(int i = 0; i < N; ++i)
        a[i] = s * b[i];
        
The code shows a simple scalar multiplication of a vector ``b`` and a floating-point number ``s``.
The result is written in vector ``a``.
After including the OSACA byte marker into the assembly, one can start the analysis typing 

.. code:: bash

    osaca --arch CSX PATH/TO/FILE

in the command line.

The output is:

.. code-block::

    Open Source Architecture Code Analyzer (OSACA) - v0.3
    Analyzed file:      scale.s.csx.O3.s
    Architecture:       csx
    Timestamp:          2019-10-03 23:36:21

     P - Throughput of LOAD operation can be hidden behind a past or future STORE instruction
     * - Instruction micro-ops not bound to a port
     X - No throughput/latency information for this instruction in data file


    Throughput Analysis Report
    --------------------------
                                  Port pressure in cycles                              
         |  0   - 0DV  |  1   |  2   -  2D  |  3   -  3D  |  4   |  5   |  6   |  7   |
    -----------------------------------------------------------------------------------
     170 |             |      |             |             |      |      |      |      |   .L22:
     171 | 0.50        | 0.50 | 0.50   0.50 | 0.50   0.50 |      |      |      |      |   vmulpd	(%r12,%rax), %ymm1, %ymm0
     172 |             |      | 0.50        | 0.50        | 1.00 |      |      |      |   vmovapd	%ymm0, 0(%r13,%rax)
     173 | 0.25        | 0.25 |             |             |      | 0.25 | 0.25 |      |   addq	$32, %rax
     174 | 0.25        | 0.25 |             |             |      | 0.25 | 0.25 |      |   cmpq	%rax, %r14
     175 |             |      |             |             |      |      |      |      | * jne	.L22

           1.00          1.00   1.00   0.50   1.00   0.50   1.00   0.50   0.50         


    Latency Analysis Report
    -----------------------
     171 |  8.0 | | vmulpd	(%r12,%rax), %ymm1, %ymm0
     172 |  5.0 | | vmovapd	%ymm0, 0(%r13,%rax)

           13.0


    Loop-Carried Dependencies Analysis Report
    -----------------------------------------
    173 |  1.0 | addq	$32, %rax                      | [173]

It shows the whole kernel together with the average port pressure of each instruction form and the overall port binding.
Furthermore, the critical path of the loop kernel and all loop-carried dependencies, each with a list of line numbers being part of this dependency chain on the right.

.. For measuring the instruction forms with ibench we highly recommend to use an exclusively allocated node, so there is no other workload falsifying the results. For the correct function of ibench the benchmark files from OSACA need to be placed in a subdirectory of src in root so ibench can create the a folder with the subdirectory’s name and the shared objects. For running the tests the frequencies of all cores must set to a constant value and this has to be given as an argument together with the directory of the shared objects to ibench, e.g.:

.. .. code:: bash

    ./ibench ./AVX 2.2
    
.. for running ibench in the directory ``AVX`` with a core frequency of 2.2 GHz. We get an output like:

.. .. code:: bash

    Using frequency 2.20GHz.
    add-mem_imd-TP: 1.023 (clock cycles) [DEBUG - result: 1.000000]
    add-mem_imd: 6.050 (clock cycles) [DEBUG - result: 1.000000]
    
.. The debug output as resulting value of register ``xmm0`` is additional validation information depending on the executed instruction form meant for the user and is not considered by OSACA. The ibench output information can be included by OSACA running the program with the flag ``--include-ibench`` or just ``-i`` and the specify micro architecture:

.. .. code-block:: bash

    osaca --arch IVB -i PATH/TO/IBENCH-OUTPUTFILE

.. For now no automatic allocation of ports for a instruction form is implemented, so for getting an output in the Ports Pressure table, one must add the port occupation by hand. We know that the inserted instruction form must be assigned always to Port 2, 3 and 4 and additionally to either 0, 1 or 5, a valid data file therefore would look like this:

.. .. code:: bash

    addl-mem_imd,1.0,6.0,"(0.33,0.33,1.00,1.00,1.00,0.33)"
    

Credits
=======
Implementation: Jan Laukemann

License
=======
`AGPL-3.0 </LICENSE>`_
