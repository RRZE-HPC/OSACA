#!/usr/bin/env python3
"""CLI for OSACA"""
import argparse
import io
import os
import re
import sys
from functools import lru_cache

from ruamel.yaml import YAML

from osaca.db_interface import import_benchmark_output, sanity_check
from osaca.frontend import Frontend
from osaca.parser import BaseParser, ParserAArch64, ParserX86ATT, ParserX86Intel
from osaca.semantics import (
    INSTR_FLAGS,
    ArchSemantics,
    KernelDG,
    MachineModel,
    reduce_to_section,
)


SUPPORTED_ARCHS = [
    "SNB",
    "IVB",
    "HSW",
    "BDW",
    "SKX",
    "CSX",
    "ICL",
    "ICX",
    "SPR",
    "ZEN1",
    "ZEN2",
    "ZEN3",
    "ZEN4",
    "TX2",
    "N1",
    "A64FX",
    "TSV110",
    "A72",
    "M1",
    "V2",
]
DEFAULT_ARCHS = {
    "aarch64": "V2",
    "x86": "SPR",
}
SUPPORTED_SYNTAXES = [
    "ATT",
    "INTEL",
]


# Stolen from pip
def __read(*names, **kwargs):
    """Reads in file"""
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
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
    return __find_version("__init__.py")


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
            description="Analyzes a marked innermost loop snippet for a given architecture type.",
            epilog="For help, examples, documentation and bug reports go to:\nhttps://github.com"
            "/RRZE-HPC/OSACA/ | License: AGPLv3",
        )

    # Add arguments
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s " + __find_version("__init__.py"),
    )
    parser.add_argument(
        "--arch",
        type=str,
        help="Define architecture (SNB, IVB, HSW, BDW, SKX, CSX, ICL, ICX, SPR, ZEN1, ZEN2, ZEN3, "
        "ZEN4, TX2, N1, A64FX, TSV110, A72, M1, V2). If no architecture is given, OSACA assumes a "
        "default uarch for x86/AArch64.",
    )
    parser.add_argument(
        "--syntax",
        type=str,
        help="Define the assembly syntax (ATT, Intel) for x86. If no syntax is given, OSACA "
        "tries to determine automatically the syntax to use.",
    )
    parser.add_argument(
        "--fixed",
        action="store_true",
        help="Run the throughput analysis with fixed probabilities for all suitable ports per "
        "instruction. Otherwise, OSACA will print the optimal port utilization for the kernel.",
    )
    parser.add_argument(
        "--lines",
        type=str,
        help="Define lines that should be included in the analysis. This option overwrites any"
        " range defined by markers in the assembly. Add either single lines or ranges defined by"
        ' "-" or ":", each entry separated by commas, e.g.: --lines 1,2,8-18,20:24',
    )
    parser.add_argument(
        "--db-check",
        dest="check_db",
        action="store_true",
        help='Run a sanity check on the by "--arch" specified database. The output depends '
        "on the verbosity level.",
    )
    parser.add_argument(
        "--online",
        dest="internet_check",
        action="store_true",
        help="Run sanity check with online DB validation (currently felixcloutier) to see the "
        "src/dst distribution of the operands. Can be only used in combination with --db-check.",
    )
    parser.add_argument(
        "--import",
        metavar="MICROBENCH",
        dest="import_data",
        type=str,
        default=argparse.SUPPRESS,
        help="Import a given microbenchmark output file into the corresponding architecture "
        'instruction database. Define the type of microbenchmark either as "ibench" or '
        '"asmbench".',
    )
    parser.add_argument(
        "--insert-marker",
        dest="insert_marker",
        action="store_true",
        help="Try to find assembly block containing the loop to analyse and insert byte "
        "marker by using Kerncraft.",
    )
    parser.add_argument(
        "--export-graph",
        metavar="EXPORT_PATH",
        dest="dotpath",
        default=None,
        type=str,
        help='Output path for .dot file export. If "." is given, the file will be stored as '
        '"./osaca_dg.dot"',
    )
    parser.add_argument(
        "--ignore-unknown",
        dest="ignore_unknown",
        action="store_true",
        help="Ignore if instructions cannot be found in the data file and print analysis anyway.",
    )
    parser.add_argument(
        "--lcd-timeout",
        dest="lcd_timeout",
        metavar="SECONDS",
        type=int,
        default=10,
        help="Set timeout in seconds for LCD analysis. After timeout, OSACA will continue"
        " its analysis with the dependency paths found up to this point. Defaults to 10."
        " Set to -1 for no timeout.",
    )
    parser.add_argument(
        "--consider-flag-deps",
        "-f",
        dest="consider_flag_deps",
        action="store_true",
        default=False,
        help="Consider flag dependencies (carry, zero, ...)",
    )
    parser.add_argument(
        "--verbose", "-v", action="count", default=0, help="Increases verbosity level."
    )
    parser.add_argument(
        "--out",
        "-o",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="Write analysis to this file (default to stdout).",
    )
    parser.add_argument(
        "--yaml-out",
        default=None,
        dest="yaml_out",
        type=argparse.FileType("w"),
        help="Write analysis as YAML representation to this file",
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Path to object (ASM or instruction file).",
    )

    return parser


def check_arguments(args, parser):
    """
    Check arguments passed by user that are not checked by argparse itself.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    :param parser: :class:`~argparse.ArgumentParser` object
    """
    supported_import_files = ["ibench", "asmbench"]

    # manually set CLX to CSX to support both abbreviations
    if args.arch and args.arch.upper() == "CLX":
        args.arch = "CSX"
    if args.arch is None and (args.check_db or "import_data" in args):
        parser.error(
            "DB check and data import cannot work with a default microarchitecture. "
            "Please see --help for all valid architecture codes."
        )
    elif args.arch is not None and args.arch.upper() not in SUPPORTED_ARCHS:
        parser.error(
            "Microarchitecture not supported. Please see --help for all valid architecture codes."
        )
    if args.syntax and args.arch and MachineModel.get_isa_for_arch(args.arch) != "x86":
        parser.error("Syntax can only be explicitly specified for an x86 microarchitecture")
    if args.syntax:
        args.syntax = args.syntax.upper()
        if args.syntax not in SUPPORTED_SYNTAXES:
            parser.error(
                "Assembly syntax not supported. Please see --help for all valid assembly syntaxes."
            )
    if "import_data" in args and args.import_data not in supported_import_files:
        parser.error(
            "Microbenchmark not supported for data import. Please see --help for all valid "
            "microbenchmark codes."
        )
    if args.internet_check and not args.check_db:
        parser.error("--online requires --check-db")


def import_data(benchmark_type, arch, filepath, output_file=sys.stdout):
    """
    Imports benchmark results from micro-benchmarks.

    :param benchmark_type: key for defining type of benchmark output
    :type benchmark_type: str
    :param arch: target architecture to put the data into the right database
    :type arch: str
    :param filepath: filepath of the output file"
    :type filepath: str
    :param output_file: output stream specifying where to write output,
                        defaults to :class:`sys.stdout`
    :type output_file: stream, optional
    """
    if benchmark_type.lower() == "ibench":
        import_benchmark_output(arch, "ibench", filepath, output=output_file)
    elif benchmark_type.lower() == "asmbench":
        import_benchmark_output(arch, "asmbench", filepath, output=output_file)
    else:
        raise NotImplementedError("This benchmark input variant is not supported.")


def insert_byte_marker(args):
    """
    Inserts byte markers into an assembly file using kerncraft.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    """
    try:
        from kerncraft.incore_model import asm_instrumentation
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
    asm_instrumentation(
        input_file=unmarked_assembly,
        output_file=marked_assembly,
        block_selection="manual",
        pointer_increment="auto_with_manual_fallback",
        isa=MachineModel.get_isa_for_arch(args.arch),
    )

    marked_assembly.seek(0)
    assembly = marked_assembly.read()
    with open(args.file.name, "w") as f:
        f.write(assembly)


def inspect(args, output_file=sys.stdout):
    """
    Does the actual throughput and critical path analysis of OSACA and prints it to the
    terminal.

    :param args: arguments given from :class:`~argparse.ArgumentParser` after parsing
    :param output_file: Define the stream for output, defaults to :class:`sys.stdout`
    :type output_file: stream, optional
    """
    # Read file
    code = args.file.read()

    # Detect ISA if necessary
    detected_isa, detected_syntax = BaseParser.detect_ISA(code)
    detected_arch = DEFAULT_ARCHS[detected_isa]

    print_arch_warning = not args.arch
    verbose = args.verbose
    ignore_unknown = args.ignore_unknown

    # If the arch/syntax is explicitly specified, that's the only thing we'll try.  Otherwise, we'll
    # look at all the possible archs/syntaxes, but with our detected arch/syntax last in the list,
    # thus tried first.
    if args.arch:
        archs_to_try = [args.arch]
    else:
        archs_to_try = list(DEFAULT_ARCHS.values())
        archs_to_try.remove(detected_arch)
        archs_to_try.append(detected_arch)
    if args.syntax:
        syntaxes_to_try = [args.syntax]
    else:
        syntaxes_to_try = SUPPORTED_SYNTAXES + [None]
        syntaxes_to_try.remove(detected_syntax)
        syntaxes_to_try.append(detected_syntax)

    # Filter the cross-product of archs and syntaxes to eliminate the combinations that don't make
    # sense.
    combinations_to_try = [
        (arch, syntax)
        for arch in archs_to_try
        for syntax in syntaxes_to_try
        if (syntax is not None) == (MachineModel.get_isa_for_arch(arch) == "x86")
    ]

    # Parse file.
    message = ""
    single_combination = len(combinations_to_try) == 1
    while True:
        arch, syntax = combinations_to_try.pop()
        parser = get_asm_parser(arch, syntax)
        try:
            parsed_code = parser.parse_file(code)
            break
        except Exception as e:
            message += f"\nWith arch {arch} and syntax {syntax} got error: {e}."
            # Either the wrong parser based on heuristic, or a bona fide syntax error (or
            # unsupported syntax).  For ease of debugging, we emit the entire exception trace if
            # we tried a single arch/syntax combination.  If we tried multiple combinations, we
            # don't emit the traceback as it would apply to the latest combination tried, which is
            # probably the less interesting.
            if not combinations_to_try:
                raise SyntaxError(message) from e if single_combination else None

    # Reduce to marked kernel or chosen section and add semantics
    if args.lines:
        line_range = get_line_range(args.lines)
        kernel = [line for line in parsed_code if line.line_number in line_range]
        print_length_warning = False
    else:
        kernel = reduce_to_section(parsed_code, parser)
        # Print warning if kernel has no markers and is larger than threshold (100)
        print_length_warning = (
            True if len(kernel) == len(parsed_code) and len(kernel) > 100 else False
        )
    machine_model = MachineModel(arch=arch)
    semantics = ArchSemantics(parser, machine_model)
    semantics.normalize_instruction_forms(kernel)
    semantics.add_semantics(kernel)
    # Do optimal schedule for kernel throughput if wished
    if not args.fixed:
        semantics.assign_optimal_throughput(kernel)
        semantics.assign_optimal_throughput(kernel)

    # Create DiGrahps
    kernel_graph = KernelDG(
        kernel, parser, machine_model, semantics, args.lcd_timeout, args.consider_flag_deps
    )
    if args.dotpath is not None:
        kernel_graph.export_graph(args.dotpath if args.dotpath != "." else None)
    # Print analysis
    frontend = Frontend(args.file.name, arch=arch)
    print(
        frontend.full_analysis(
            kernel,
            kernel_graph,
            ignore_unknown=ignore_unknown,
            arch_warning=print_arch_warning,
            length_warning=print_length_warning,
            lcd_warning=kernel_graph.timed_out,
            verbose=verbose,
        ),
        file=output_file,
    )
    if args.yaml_out is not None:
        yaml = YAML(typ="unsafe", pure=True)
        yaml.dump(
            frontend.full_analysis_dict(
                kernel,
                kernel_graph,
                arch_warning=print_arch_warning,
                length_warning=print_length_warning,
                lcd_warning=kernel_graph.timed_out,
            ),
            args.yaml_out,
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
            args.arch,
            verbose=verbose,
            internet_check=args.internet_check,
            output_file=output_file,
        )
    elif "import_data" in args:
        # Import microbench output file into DB
        import_data(args.import_data, args.arch, args.file.name, output_file=output_file)
    elif args.insert_marker:
        # Try to add IACA marker
        insert_byte_marker(args)
    else:
        # Analyze kernel
        inspect(args, output_file=output_file)


@lru_cache()
def get_asm_parser(arch, syntax="ATT") -> BaseParser:
    """
    Helper function to create the right parser for a specific architecture.

    :param arch: architecture code
    :type arch: str
    :returns: :class:`~osaca.parser.BaseParser` object
    """
    isa = MachineModel.get_isa_for_arch(arch)
    if isa == "x86":
        return ParserX86ATT() if syntax == "ATT" else ParserX86Intel()
    elif isa == "aarch64":
        return ParserAArch64()


def get_unmatched_instruction_ratio(kernel):
    """Return ratio of unmatched from total instructions in kernel."""
    unmatched_counter = 0
    for instruction in kernel:
        if INSTR_FLAGS.TP_UNKWN in instruction.flags and INSTR_FLAGS.LT_UNKWN in instruction.flags:
            unmatched_counter += 1
    return unmatched_counter / len(kernel)


def get_line_range(line_str):
    line_str = line_str.replace(":", "-")
    lines = line_str.split(",")
    lines_int = []
    for line in lines:
        if "-" in line:
            start = int(line.split("-")[0])
            end = int(line.split("-")[1])
            rnge = list(range(start, end + 1))
            lines_int += rnge
        else:
            lines_int.append(int(line))
    return lines_int


def main():
    """Initialize and run command line interface."""
    parser = create_parser()
    args = parser.parse_args()
    check_arguments(args, parser)
    run(args, output_file=args.out)


if __name__ == "__main__":
    main()
