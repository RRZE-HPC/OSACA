#!/usr/bin/env python3

import argparse
import io
import os
import re
import sys
from filecmp import dircmp
from subprocess import call

from osaca.api import sanity_check
from osaca.frontend import Frontend
from osaca.parser import BaseParser, ParserAArch64v81, ParserX86ATT
from osaca.semantics import (KernelDG, MachineModel, SemanticsAppender,
                             reduce_to_section)

MODULE_DATA_DIR = os.path.join(
    os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), 'osaca/data/'
)
DATA_DIR = os.path.expanduser('~') + '/.osaca/data/'


# Stolen from pip
def __read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


# Stolen from pip
def __find_version(*file_paths):
    version_file = __read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def get_version():
    return __find_version('__init__.py')


def create_parser():
    """Return argparse parser."""
    # Create parser
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
        help='Define architecture (SNB, IVB, HSW, BDW, SKX, CSX, ZEN1, VULCAN).',
    )
    parser.add_argument(
        '--db-check',
        dest='check_db',
        action='store_true',
        help='Run a sanity check on the by "--arch" specified database. The output depends '
        'on the verbosity level.',
    )
    parser.add_argument(
        '--import',
        metavar='MICROBENCH',
        dest='import_data',
        type=str,
        default=argparse.SUPPRESS,
        help='Import a given microbenchmark output file into the corresponding architecture '
        'instruction database. Define the type of microbenchmark either as "ibench", '
        '"asmbench" or "uopsinfo".',
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
        '--verbose', '-v', action='count', default=0, help='Increases verbosity level.'
    )
    parser.add_argument(
        'file', type=argparse.FileType('r'), help='Path to object (ASM or instruction file).'
    )

    return parser


def check_arguments(args, parser):
    """Check arguments passed by user that are not checked by argparse itself."""
    supported_archs = ['SNB', 'IVB', 'HSW', 'BDW', 'SKX', 'CSX', 'ZEN1', 'VULCAN']
    supported_import_files = ['ibench', 'asmbench', 'uopsinfo']

    if 'arch' in args and args.arch.upper() not in supported_archs:
        parser.error(
            'Microarchitecture not supported. Please see --help for all valid architecture codes.'
        )
    if 'import_data' in args and args.import_data not in supported_import_files:
        parser.error(
            'Microbenchmark not supported for data import. Please see --help for all valid '
            'microbenchmark codes.'
        )


def check_user_dir():
    # Check if data files are already in usr dir, otherwise create them
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
        call(['cp', '-r', MODULE_DATA_DIR, DATA_DIR])
    else:
        # Compare and warn if files in DATA_DIR are different
        dir_comp = dircmp(DATA_DIR, MODULE_DATA_DIR)
        if dir_comp.left_list != dir_comp.same_files:
            print(
                "WARNING: Files in {} differs from {}. Check or delete {}.".format(
                    MODULE_DATA_DIR, DATA_DIR, DATA_DIR
                ),
                file=sys.stderr,
            )


def import_data(benchmark_type, filepath):
    raise NotImplementedError


def insert_byte_marker(args):
    if MachineModel.get_isa_for_arch(args.arch) != 'x86':
        print('Marker insertion for non-x86 is not yet supported by Kerncraft.', file=sys.stderr)
        sys.exit(1)
    try:
        from kerncraft import iaca
    except ImportError:
        print(
            "Module kerncraft not installed. Use 'pip install --user "
            "kerncraft' for installation.\nFor more information see "
            "https://github.com/RRZE-HPC/kerncraft",
            file=sys.stderr,
        )
        sys.exit(1)

    assembly = args.file.read()
    unmarked_assembly = io.StringIO(assembly)
    marked_assembly = io.StringIO()
    iaca.iaca_instrumentation(
        input_file=unmarked_assembly,
        output_file=marked_assembly,
        block_selection='manual',
        pointer_increment='auto_with_manual_fallback',
    )

    marked_assembly.seek(0)
    assembly = marked_assembly.read()
    with open(args.file.name, 'w') as f:
        f.write(assembly)


def inspect(args):
    arch = args.arch
    isa = MachineModel.get_isa_for_arch(arch)
    verbose = args.verbose

    # Read file
    code = args.file.read()
    # Parse file
    parser = _create_parser(arch)
    parsed_code = parser.parse_file(code)

    # Reduce to marked kernel and add semantics
    kernel = reduce_to_section(parsed_code, isa)
    machine_model = MachineModel(arch=arch)
    semantics = SemanticsAppender(machine_model)
    semantics.add_semantics(kernel)

    # Create DiGrahps
    kernel_graph = KernelDG(kernel, parser, machine_model)
    if args.dotpath is not None:
        kernel_graph.export_graph(args.dotpath if args.dotpath != '.' else None)
    # Print analysis
    frontend = Frontend(args.file.name, arch=arch)
    frontend.print_full_analysis(kernel, kernel_graph, verbose=verbose)


def run(args, output_file=sys.stdout):
    if args.check_db:
        # Sanity check on DB
        verbose = True if args.verbose > 0 else False
        sanity_check(args.arch, verbose=verbose)
    if 'import_data' in args:
        # Import microbench output file into DB
        import_data(args.import_data, args.file)
    if args.insert_marker:
        # Try to add IACA marker
        insert_byte_marker(args)
    else:
        # Analyze kernel
        inspect(args)


# ---------------------------------------------------
def _create_parser(arch) -> BaseParser:
    isa = MachineModel.get_isa_for_arch(arch)
    if isa == 'x86':
        return ParserX86ATT()
    elif isa == 'aarch64':
        return ParserAArch64v81()


# ---------------------------------------------------


def main():
    """Initialize and run command line interface."""
    parser = create_parser()
    args = parser.parse_args()
    check_arguments(args, parser)
    check_user_dir()
    run(args)


if __name__ == '__main__':
    main()
