#!/usr/bin/env python3
from collections import OrderedDict

from osaca.parser import ParserAArch64v81, ParserX86ATT, get_parser

COMMENT_MARKER = {'start': 'OSACA-BEGIN', 'end': 'OSACA-END'}


def reduce_to_section(kernel, isa):
    """
    Finds OSACA markers in given kernel and returns marked section

    :param list kernel: kernel to check
    :param str isa: ISA of given kernel
    :returns: `list` -- marked section of kernel as list of instruction forms
    """
    isa = isa.lower()
    if isa == 'x86':
        start, end = find_marked_kernel_x86ATT(kernel)
    elif isa == 'aarch64':
        start, end = find_marked_kernel_AArch64(kernel)
    else:
        raise ValueError('ISA not supported.')
    if start == -1:
        raise LookupError('Could not find START MARKER. Make sure it is inserted!')
    if end == -1:
        raise LookupError('Could not find END MARKER. Make sure it is inserted!')
    return kernel[start:end]


def find_marked_kernel_AArch64(lines):
    """
    Find marked section for AArch64

    :param list lines: kernel
    :returns: `tuple of int` -- start and end line of marked section
    """
    nop_bytes = ['213', '3', '32', '31']
    return find_marked_section(
        lines,
        ParserAArch64v81(),
        ['mov'],
        'x1',
        [111, 222],
        nop_bytes,
        reverse=True,
        comments=COMMENT_MARKER,
    )


def find_marked_kernel_x86ATT(lines):
    """
    Find marked section for x86

    :param list lines: kernel
    :returns: `tuple of int` -- start and end line of marked section
    """
    nop_bytes = ['100', '103', '144']
    return find_marked_section(
        lines,
        ParserX86ATT(),
        ['mov', 'movl'],
        'ebx',
        [111, 222],
        nop_bytes,
        comments=COMMENT_MARKER,
    )


def get_marker(isa, comment=""):
    """Return tuple of start and end marker lines."""
    isa = isa.lower()
    if isa == 'x86':
        start_marker_raw = (
            'movl      $111, %ebx # OSACA START MARKER\n'
            '.byte     100        # OSACA START MARKER\n'
            '.byte     103        # OSACA START MARKER\n'
            '.byte     144        # OSACA START MARKER\n'
        )
        if comment:
            start_marker_raw += "# {}\n".format(comment)
        end_marker_raw = (
            'movl      $222, %ebx # OSACA END MARKER\n'
            '.byte     100        # OSACA END MARKER\n'
            '.byte     103        # OSACA END MARKER\n'
            '.byte     144        # OSACA END MARKER\n'
        )
    elif isa == 'aarch64':
        start_marker_raw = (
            'mov       x1, #111    // OSACA START MARKER\n'
            '.byte     213,3,32,31 // OSACA START MARKER\n'
        )
        if comment:
            start_marker_raw += "// {}\n".format(comment)
        # After loop
        end_marker_raw = (
            'mov       x1, #222    // OSACA END MARKER\n'
            '.byte     213,3,32,31 // OSACA END MARKER\n'
        )

    parser = get_parser(isa)
    start_marker = parser.parse_file(start_marker_raw)
    end_marker = parser.parse_file(end_marker_raw)

    return start_marker, end_marker


def find_marked_section(
    lines, parser, mov_instr, mov_reg, mov_vals, nop_bytes, reverse=False, comments=None
):
    """
    Return indexes of marked section

    :param list lines: kernel
    :param parser: parser to use for checking
    :type parser: :class:`~parser.BaseParser`
    :param mov_instr: all MOV instruction possible for the marker
    :type mov_instr: `list of str`
    :param mov_reg: register used for the marker
    :type mov_reg: `str`
    :param mov_vals: values needed to be moved to ``mov_reg`` for valid marker
    :type mov_vals: `list of int`
    :param nop_bytes: bytes representing opcode of NOP
    :type nop_bytes: `list of int`
    :param reverse: indicating if ISA syntax requires reverse operand order, defaults to `False`
    :type reverse: boolean, optional
    :param comments: dictionary with start and end markers in comment format, defaults to None
    :type comments: dict, optional
    :returns: `tuple of int` -- start and end line of marked section
    """
    # TODO match to instructions returned by get_marker
    index_start = -1
    index_end = -1
    for i, line in enumerate(lines):
        try:
            if line.instruction is None and comments is not None and line.comment is not None:
                if comments['start'] == line.comment:
                    index_start = i + 1
                elif comments['end'] == line.comment:
                    index_end = i
            elif line.instruction in mov_instr and lines[i + 1].directive is not None:
                source = line.operands[0 if not reverse else 1]
                destination = line.operands[1 if not reverse else 0]
                # instruction pair matches, check for operands
                if (
                    'immediate' in source
                    and parser.normalize_imd(source.immediate) == mov_vals[0]
                    and 'register' in destination
                    and parser.get_full_reg_name(destination.register) == mov_reg
                ):
                    # operands of first instruction match start, check for second one
                    match, line_count = match_bytes(lines, i + 1, nop_bytes)
                    if match:
                        # return first line after the marker
                        index_start = i + 1 + line_count
                elif (
                    'immediate' in source
                    and parser.normalize_imd(source.immediate) == mov_vals[1]
                    and 'register' in destination
                    and parser.get_full_reg_name(destination.register) == mov_reg
                ):
                    # operand of first instruction match end, check for second one
                    match, line_count = match_bytes(lines, i + 1, nop_bytes)
                    if match:
                        # return line of the marker
                        index_end = i
        except TypeError:
            print(i, line)
        if index_start != -1 and index_end != -1:
            break
    return index_start, index_end


def match_bytes(lines, index, byte_list):
    """Match bytes directives of markers"""
    # either all bytes are in one line or in separate ones
    extracted_bytes = []
    line_count = 0
    while (
        index < len(lines)
        and lines[index].directive is not None
        and lines[index].directive.name == 'byte'
    ):
        line_count += 1
        extracted_bytes += lines[index].directive.parameters
        index += 1
    if extracted_bytes[0 : len(byte_list)] == byte_list:
        return True, line_count
    return False, -1


def find_jump_labels(lines):
    """
    Find and return all labels which are followed by instructions until the next label

    :return: OrderedDict of mapping from label name to associated line index
    """
    # 1. Identify labels and instructions until next label
    labels = OrderedDict()
    current_label = None
    for i, line in enumerate(lines):
        if line['label'] is not None:
            # When a new label is found, add to blocks dict
            labels[line['label']] = (i,)
            # End previous block at previous line
            if current_label is not None:
                labels[current_label] = (labels[current_label][0], i)
            # Update current block name
            current_label = line['label']
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
                l['instruction'].startswith('.')
                for l in lines[labels[label][0] : labels[label][1]]
                if l['instruction'] is not None
            ]
        ):
            del labels[label]

    return OrderedDict([(l, v[0]) for l, v in labels.items()])


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
            if line['instruction'] and line['operands']:
                for operand in [o for o in line['operands'] if 'identifier' in o]:
                    if operand['identifier']['name'] in valid_jump_labels:
                        terminate = True
            elif line['label'] is not None:
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
            if line['instruction'] and line['operands']:
                for operand in [o for o in line['operands'] if 'identifier' in o]:
                    if operand['identifier']['name'] in valid_jump_labels:
                        if operand['identifier']['name'] == label:
                            loop_bodies[label] = current_block
                        terminate = True
                        break
            if terminate:
                break

    return loop_bodies
