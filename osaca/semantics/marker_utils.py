#!/usr/bin/env python3

from osaca.parser import ParserAArch64v81, ParserX86ATT


def reduce_to_section(kernel, isa):
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
    nop_bytes = ['213', '3', '32', '31']
    return find_marked_kernel(
        lines, ParserAArch64v81(), ['mov'], 'x1', [111, 222], nop_bytes, reverse=True
    )


def find_marked_kernel_x86ATT(lines):
    nop_bytes = ['100', '103', '144']
    return find_marked_kernel(lines, ParserX86ATT(), ['mov', 'movl'], 'ebx', [111, 222], nop_bytes)


def find_marked_kernel(lines, parser, mov_instr, mov_reg, mov_vals, nop_bytes, reverse=False):
    index_start = -1
    index_end = -1
    for i, line in enumerate(lines):
        try:
            if line.instruction in mov_instr and lines[i + 1].directive is not None:
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
    if extracted_bytes[0:len(byte_list)] == byte_list:
        return True, line_count
    return False, -1
