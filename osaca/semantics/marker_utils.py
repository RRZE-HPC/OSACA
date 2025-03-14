#!/usr/bin/env python3
from collections import OrderedDict
from enum import Enum

from osaca.parser import get_parser
from osaca.parser.identifier import IdentifierOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand

COMMENT_MARKER = {"start": "OSACA-BEGIN", "end": "OSACA-END"}


# State of marker matching.
#   No: we have determined that the code doesn't match the marker.
#   Partial: so far the code matches the marker, but we have not reached the end of the marker yet.
#   Full: the code matches all instructions in the marker.
class Matching(Enum):
    No = 0
    Partial = 1
    Full = 2


def reduce_to_section(kernel, parser):
    """
    Finds OSACA markers in given kernel and returns marked section

    :param list kernel: kernel to check
    :param BaseParser parser: parser used to produce the kernel
    :returns: `list` -- marked section of kernel as list of instruction forms
    """
    start, end = find_marked_section(kernel, parser, COMMENT_MARKER)
    if start == -1:
        start = 0
    if end == -1:
        end = len(kernel)
    return kernel[start:end]


def find_marked_section(lines, parser, comments=None):
    """
    Return indexes of marked section

    :param list lines: kernel
    :param parser: parser to use for checking
    :type parser: :class:`~parser.BaseParser`
    :param comments: dictionary with start and end markers in comment format, defaults to None
    :type comments: dict, optional
    :returns: `tuple of int` -- start and end line of marked section
    """
    index_start = -1
    index_end = -1
    start_marker = parser.start_marker()
    end_marker = parser.end_marker()
    for i, line in enumerate(lines):
        try:
            if line.mnemonic is None and comments is not None and line.comment is not None:
                if comments["start"] == line.comment:
                    index_start = i + 1
                elif comments["end"] == line.comment:
                    index_end = i
            if index_start == -1:
                matching_lines = match_lines(parser, lines[i:], start_marker)
                if matching_lines > 0:
                    # Return the first line after the marker.
                    index_start = i + matching_lines
            if index_end == -1:
                if match_lines(parser, lines[i:], end_marker):
                    index_end = i
        except TypeError as e:
            print(i, e, line)
        if index_start != -1 and index_end != -1:
            break
    return index_start, index_end


# This function and the following ones traverse the syntactic tree produced by the parser and try to
# match it to the marker.  This is necessary because the IACA markers are significantly different on
# MSVC x86 than on other ISA/compilers.  Therefore, simple string matching is not sufficient.  Also,
# the syntax of numeric literals depends on the parser and should not be known to this class.
# The matching only checks for a limited number of properties (and the marker doesn't specify the
# rest).
def match_lines(parser, lines, marker):
    """
    Returns True iff the `lines` match the `marker`.

    :param list of `InstructionForm` lines: parsed assembly code.
    :param list of `InstructionForm` marker: pattern to match against the `lines`.
    :return int: the length of the match in the parsed code, 0 if there is no match.
    """
    marker_iter = iter(marker)
    marker_line = next(marker_iter)
    for matched_lines, line in enumerate(lines):
        if isinstance(marker_line, list):
            # No support for partial matching in lists.
            for marker_alternative in marker_line:
                matching = match_line(parser, line, marker_alternative)
                if matching == Matching.Full:
                    break
            else:
                return 0
            marker_line = next(marker_iter, None)
        else:
            matching = match_line(parser, line, marker_line)
            if matching == Matching.No:
                return 0
            elif matching == Matching.Partial:
                # Try the same marker line again.  The call to `match_line` consumed some of the
                # directive parameters.
                pass
            elif matching == Matching.Full:
                # Move to the next marker line, the current one has been fully matched.
                marker_line = next(marker_iter, None)
        # If we have reached the last marker line, the parsed code matches the marker.
        if not marker_line:
            return matched_lines + 1


def get_marker(isa, syntax="ATT", comment=""):
    """Return tuple of start and end marker lines."""
    isa = isa.lower()
    syntax = syntax.lower()
    if isa == "x86":
        if syntax == "att":
            start_marker_raw = (
                "movl      $111, %ebx # OSACA START MARKER\n"
                ".byte     100        # OSACA START MARKER\n"
                ".byte     103        # OSACA START MARKER\n"
                ".byte     144        # OSACA START MARKER\n"
            )
            if comment:
                start_marker_raw += "# {}\n".format(comment)
            end_marker_raw = (
                "movl      $222, %ebx # OSACA END MARKER\n"
                ".byte     100        # OSACA END MARKER\n"
                ".byte     103        # OSACA END MARKER\n"
                ".byte     144        # OSACA END MARKER\n"
            )
        else:
            # Intel syntax
            start_marker_raw = (
                "movl      ebx, 111   # OSACA START MARKER\n"
                ".byte     100        # OSACA START MARKER\n"
                ".byte     103        # OSACA START MARKER\n"
                ".byte     144        # OSACA START MARKER\n"
            )
            if comment:
                start_marker_raw += "# {}\n".format(comment)
            end_marker_raw = (
                "movl      ebx, 222   # OSACA END MARKER\n"
                ".byte     100        # OSACA END MARKER\n"
                ".byte     103        # OSACA END MARKER\n"
                ".byte     144        # OSACA END MARKER\n"
            )
    elif isa == "aarch64":
        start_marker_raw = (
            "mov       x1, #111    // OSACA START MARKER\n"
            ".byte     213,3,32,31 // OSACA START MARKER\n"
        )
        if comment:
            start_marker_raw += "// {}\n".format(comment)
        # After loop
        end_marker_raw = (
            "mov       x1, #222    // OSACA END MARKER\n"
            ".byte     213,3,32,31 // OSACA END MARKER\n"
        )

    parser = get_parser(isa)
    start_marker = parser.parse_file(start_marker_raw)
    end_marker = parser.parse_file(end_marker_raw)

    return start_marker, end_marker


def match_line(parser, line, marker_line):
    """
    Returns whether `line` matches `marker_line`.

    :param `IntructionForm` line: parsed assembly code.
    :param marker_line `InstructionForm` marker: pattern to match against `line`.
    :return: Matching. In case of partial match, `marker_line` is modified and should be reused for
                       matching the next line in the parsed assembly code.
    """
    if (
        line.mnemonic
        and marker_line.mnemonic
        and line.mnemonic == marker_line.mnemonic
        and match_operands(line.operands, marker_line.operands)
    ):
        return Matching.Full
    if (
        line.directive
        and marker_line.directive
        and line.directive.name == marker_line.directive.name
    ):
        return match_parameters(
            parser, line.directive.parameters, marker_line.directive.parameters
        )
    else:
        return Matching.No


def match_operands(line_operands, marker_line_operands):
    if len(line_operands) != len(marker_line_operands):
        return False
    return all(
        match_operand(line_operand, marker_line_operand)
        for line_operand, marker_line_operand in zip(line_operands, marker_line_operands)
    )


def match_operand(line_operand, marker_line_operand):
    if (
        isinstance(line_operand, ImmediateOperand)
        and isinstance(marker_line_operand, ImmediateOperand)
        and line_operand.value == marker_line_operand.value
    ):
        return True
    if (
        isinstance(line_operand, RegisterOperand)
        and isinstance(marker_line_operand, RegisterOperand)
        and line_operand.name.lower() == marker_line_operand.name.lower()
    ):
        return True
    if (
        isinstance(line_operand, MemoryOperand)
        and isinstance(marker_line_operand, MemoryOperand)
        and match_operand(line_operand.base, marker_line_operand.base)
        and match_operand(line_operand.offset, line_operand.offset)
    ):
        return True
    return False


def match_parameters(parser, line_parameters, marker_line_parameters):
    """
    Returns whether `line_parameters` matches `marker_line_parameters`.

    :param list of strings line_parameters: parameters of a directive in the parsed assembly code.
    :param list of strings marker_line_parameters: parameters of a directive in the marker.
    :return: Matching. In case of partial match, `marker_line_parameters` is modified and should be
                       reused for matching the next line in the parsed assembly code.
    """
    # The elements of `marker_line_parameters` are consumed as they are matched.
    for line_parameter in line_parameters:
        if not marker_line_parameters:
            break
        marker_line_parameter = marker_line_parameters[0]
        if not match_parameter(parser, line_parameter, marker_line_parameter):
            return Matching.No
        marker_line_parameters.pop(0)
    if marker_line_parameters:
        return Matching.Partial
    else:
        return Matching.Full


def match_parameter(parser, line_parameter, marker_line_parameter):
    if line_parameter.lower() == marker_line_parameter.lower():
        return True
    else:
        # If the parameters don't match verbatim, check if they represent the same immediate value.
        line_immediate = ImmediateOperand(value=line_parameter)
        marker_line_immediate = ImmediateOperand(value=marker_line_parameter)
        return parser.normalize_imd(line_immediate) == parser.normalize_imd(marker_line_immediate)


def find_jump_labels(lines):
    """
    Find and return all labels which are followed by instructions until the next label

    :return: OrderedDict of mapping from label name to associated line index
    """
    # 1. Identify labels and instructions until next label
    labels = OrderedDict()
    current_label = None
    for i, line in enumerate(lines):
        if line.label is not None:
            # When a new label is found, add to blocks dict
            labels[line.label] = (i,)
            # End previous block at previous line
            if current_label is not None:
                labels[current_label] = (labels[current_label][0], i)
            # Update current block name
            current_label = line.label
        elif current_label is None:
            # If no block has been started, skip end detection
            continue
    # Set to last line if no end was for last label found
    if current_label is not None and len(labels[current_label]) == 1:
        labels[current_label] = (labels[current_label][0], len(lines))

    # 2. Identify and remove labels which contain only dot-instructions (e.g., .text)
    for label in list(labels):
        if all(
            [
                line.mnemonic.startswith(".")
                for line in lines[labels[label][0] : labels[label][1]]
                if line.mnemonic is not None
            ]
        ):
            del labels[label]

    return OrderedDict([(label, v[0]) for label, v in labels.items()])


def find_basic_blocks(lines):
    """
    Find and return basic blocks (asm sections which can only be executed as complete block).

    Blocks always start at a label and end at the next jump/break possibility.

    :return: OrderedDict with labels as keys and list of lines as value
    """
    valid_jump_labels = find_jump_labels(lines)

    # Identify blocks, as they are started with a valid jump label and terminated by a label or
    # an instruction referencing a valid jump label
    blocks = OrderedDict()
    for label, label_line_idx in valid_jump_labels.items():
        blocks[label] = [lines[label_line_idx]]
        for line in lines[label_line_idx + 1 :]:
            terminate = False
            blocks[label].append(line)
            # Find end of block by searching for references to valid jump labels
            if line.mnemonic is not None and line.operands != []:
                for operand in [o for o in line.operands if isinstance(o, IdentifierOperand)]:
                    if operand.name in valid_jump_labels:
                        terminate = True
            elif line.label is not None:
                terminate = True
            if terminate:
                break

    return blocks


def find_basic_loop_bodies(lines):
    """
    Find and return basic loop bodies (asm section which loop back on itself with no other egress).

    :return: OrderedDict with labels as keys and list of lines as value
    """
    valid_jump_labels = find_jump_labels(lines)

    # Identify blocks, as they are started with a valid jump label and terminated by
    # an instruction referencing a valid jump label
    loop_bodies = OrderedDict()
    for label, label_line_idx in valid_jump_labels.items():
        current_block = [lines[label_line_idx]]
        for line in lines[label_line_idx + 1 :]:
            terminate = False
            current_block.append(line)
            # Find end of block by searching for references to valid jump labels
            if line.mnemonic is not None and line.operands != []:
                # Ignore `b.none` instructions (relevant von ARM SVE code)
                # This branch instruction is often present _within_ inner loop blocks, but usually
                # do not terminate
                if line.mnemonic == "b.none":
                    continue
                for operand in [o for o in line.operands if isinstance(o, IdentifierOperand)]:
                    if operand.name in valid_jump_labels:
                        if operand.name == label:
                            loop_bodies[label] = current_block
                        terminate = True
                        break
            if terminate:
                break

    return loop_bodies
