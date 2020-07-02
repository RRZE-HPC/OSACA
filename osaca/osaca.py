#!/usr/bin/env python3
"""CLI for OSACA"""
import argparse
import io
import os
import re
import sys

from osaca.db_interface import import_benchmark_output, sanity_check
from osaca.frontend import Frontend
from osaca.parser import BaseParser, ParserAArch64v81, ParserX86ATT
from osaca.semantics import (INSTR_FLAGS, ArchSemantics, KernelDG,
                             MachineModel, reduce_to_section)

MODULE_DATA_DIR = os.path.join(
    os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), 'osaca/data/'
)
LOCAL_OSACA_DIR = os.path.join(os.path.expanduser('~') + '/.osaca/')
DATA_DIR = os.path.join(LOCAL_OSACA_DIR, 'data/')
SUPPORTED_ARCHS = ['SNB', 'IVB', 'HSW', 'BDW', 'SKX', 'CSX', 'ZEN1', 'ZEN2', 'TX2', 'N1']


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
    raise RuntimeError('Unable to find version string.')


def get_version():
    """
    Gets the current OSACA version stated in the __init__ file

    :returns: str -- the version string.
    """
    return __find_version('__init__.py')


def create_parser(parser=None):
    """
    Return argparse parser.

    :param parser: Existing parser object to add the arguments, defaults to `None`
    :type parser: :class:`~Argparse.ArgumentParser`
    :returns: The newly created :class:`~Argparse.ArgumentParser` object.
    """
    # Create parser
    if not parser:
        parser = argparse.ArgumentParser(
            description='Analyzes a marked innermost loop snippet for a given architecture type.',
            epilog='For help, examples, documentation and bug reports go to:\nhttps://github.com'
            '/RRZE-HPC/OSACA/ | License: AGPLv3',
        )

    # Add arguments
    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s ' + __find_version('__init__.py')
    )
    parser.add_argument(
        '--arch',
        type=str,
        help='Define architecture (SNB, IVB, HSW, BDW, SKX, CSX, ZEN1, ZEN2, TX2, N1).',
    )
    parser.add_argument(
        '--fixed',
        action='store_true',
        help='Run the throughput analysis with fixed probabilities for all suitable ports per '
        'instruction. Otherwise, OSACA will print the optimal port utilization for the kernel.',
    )
    parser.add_argument(
        '--db-check',
        dest='check_db',
        action='store_true',
        help='Run a sanity check on the by "--arch" specified database. The output depends '
        'on the verbosity level.',
    )
    parser.add_argument(
        '--online',
        dest='internet_check',
        action='store_true',
        help='Run sanity check with online DB validation (currently felixcloutier) to see the '
        'src/dst distribution of the operands. Can be only used in combination with --db-check.',
    )
    parser.add_argument(
        '--import',
        metavar='MICROBENCH',
        dest='import_data',
        type=str,
        default=argparse.SUPPRESS,
        help='Import a given microbenchmark output file into the corresponding architecture '
        'instruction database. Define the type of microbenchmark either as "ibench" or '
        '"asmbench".',
    )
    parser.add_argument(
        '--insert-marker',
        dest='insert_marker',
        action='store_true',
        help='Try to find assembly block containing the loop to analyse and insert byte '
        'marker by using Kerncraft.',
    )
    parser.add_argument(
        '--export-graph',
        metavar='EXPORT_PATH',
        dest='dotpath',
        default=None,
        type=str,
        help='Output path for .dot file export. If "." is given, the file will be stored as '
        '"./osaca_dg.dot"',
    )
    parser.add_argument(
        '--ignore-unknown',
        dest='ignore_unknown',
        action='store_true',
        help='Ignore if instructions cannot be found in the data file and print analysis anyway.',
    )
    parser.add_argument(
        '--verbose', '-v', action='count', default=0, help='Increases verbosity level.'
    )
    parser.add_argument(
        'file', type=argparse.FileType('r'), help='Path to object (ASM or instruction file).'
    )

    return parser


def check_arguments(args, parser):
    """
    Check arguments passed by user that are not checked by argparse itself.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    :param parser: :class:`~argparse.ArgumentParser` object
    """
    supported_import_files = ['ibench', 'asmbench']

    if 'arch' in args and (args.arch is None or args.arch.upper() not in SUPPORTED_ARCHS):
        parser.error(
            'Microarchitecture not supported. Please see --help for all valid architecture codes.'
        )
    if 'import_data' in args and args.import_data not in supported_import_files:
        parser.error(
            'Microbenchmark not supported for data import. Please see --help for all valid '
            'microbenchmark codes.'
        )
    if args.internet_check and not args.check_db:
        parser.error('--online requires --check-db')


def import_data(benchmark_type, arch, filepath, output_file=sys.stdout):
    """
    Imports benchmark results from micro-benchmarks.

    :param benchmark_type: key for defining type of benchmark output
    :type benchmark_type: str
    :param arch: target architecture to put the data into the right database
    :type arch: str
    :param filepath: filepath of the output file"
    :type filepath: str
    :param output_file: output stream specifying where to write output, defaults to :class:`sys.stdout`
    :type output_file: stream, optional
    """
    if benchmark_type.lower() == 'ibench':
        import_benchmark_output(arch, 'ibench', filepath, output=output_file)
    elif benchmark_type.lower() == 'asmbench':
        import_benchmark_output(arch, 'asmbench', filepath, output=output_file)
    else:
        raise NotImplementedError('This benchmark input variant is not supported.')


def insert_byte_marker(args):
    """
    Inserts byte markers into an assembly file using kerncraft.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    """
    try:
        from kerncraft.incore_model import asm_instrumentation
    except ImportError:
        print(
            'Module kerncraft not installed. Use \'pip install --user '
            'kerncraft\' for installation.\nFor more information see '
            'https://github.com/RRZE-HPC/kerncraft',
            file=sys.stderr,
        )
        sys.exit(1)

    assembly = args.file.read()
    unmarked_assembly = io.StringIO(assembly)
    marked_assembly = io.StringIO()
    asm_instrumentation(
        input_file=unmarked_assembly,
        output_file=marked_assembly,
        block_selection='manual',
        pointer_increment='auto_with_manual_fallback',
        isa=MachineModel.get_isa_for_arch(args.arch),
    )

    marked_assembly.seek(0)
    assembly = marked_assembly.read()
    with open(args.file.name, 'w') as f:
        f.write(assembly)


def inspect(args, output_file=sys.stdout):
    """
    Does the actual throughput and critical path analysis of OSACA and prints it to the
    terminal.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    :param output_file: Define the stream for output, defaults to :class:`sys.stdout`
    :type output_file: stream, optional
    """
    arch = args.arch
    isa = MachineModel.get_isa_for_arch(arch)
    verbose = args.verbose
    ignore_unknown = args.ignore_unknown

    # Read file
    code = args.file.read()
    # Parse file
    parser = get_asm_parser(arch)
    parsed_code = parser.parse_file(code)

    # Reduce to marked kernel and add semantics
    kernel = reduce_to_section(parsed_code, isa)
    machine_model = MachineModel(arch=arch)
    semantics = ArchSemantics(machine_model)
    semantics.add_semantics(kernel)
    # Do optimal schedule for kernel throughput if wished
    if not args.fixed:
        semantics.assign_optimal_throughput(kernel)

    # Create DiGrahps
    kernel_graph = KernelDG(kernel, parser, machine_model)
    if args.dotpath is not None:
        kernel_graph.export_graph(args.dotpath if args.dotpath != '.' else None)
    # Print analysis
    frontend = Frontend(args.file.name, arch=arch)
    print(
        frontend.full_analysis(
            kernel, kernel_graph, ignore_unknown=ignore_unknown, verbose=verbose
        ),
        file=output_file,
    )


def run(args, output_file=sys.stdout):
    """
    Main entry point for OSACAs workflow. Decides whether to run an analysis or other things.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    :param output_file: Define the stream for output, defaults to :class:`sys.stdout`
    :type output_file: stream, optional
    """
    if args.check_db:
        # Sanity check on DB
        verbose = True if args.verbose > 0 else False
        sanity_check(
            args.arch, verbose=verbose, internet_check=args.internet_check, output_file=output_file
        )
    elif 'import_data' in args:
        # Import microbench output file into DB
        import_data(args.import_data, args.arch, args.file.name, output_file=output_file)
    elif args.insert_marker:
        # Try to add IACA marker
        insert_byte_marker(args)
    else:
        # Analyze kernel
        inspect(args, output_file=output_file)


def get_asm_parser(arch) -> BaseParser:
    """
    Helper function to create the right parser for a specific architecture.

    :param arch: architecture code
    :type arch: str
    :returns: :class:`~osaca.parser.BaseParser` object
    """
    isa = MachineModel.get_isa_for_arch(arch)
    if isa == 'x86':
        return ParserX86ATT()
    elif isa == 'aarch64':
        return ParserAArch64v81()


def get_unmatched_instruction_ratio(kernel):
    """Return ratio of unmatched from total instructions in kernel."""
    unmatched_counter = 0
    for instruction in kernel:
        if (
            INSTR_FLAGS.TP_UNKWN in instruction['flags']
            and INSTR_FLAGS.LT_UNKWN in instruction['flags']
        ):
            unmatched_counter += 1
    return unmatched_counter / len(kernel)


def main():
    """Initialize and run command line interface."""
    parser = create_parser()
    args = parser.parse_args()
    check_arguments(args, parser)
    run(args)


if __name__ == '__main__':
    main()
