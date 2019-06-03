#!/usr/bin/env python3

from osaca.parser import ParserAArch64v81, ParserX86ATT


class Analyzer(object):
    def __init__(self, parser_result, isa):
        if isa == 'x86':
            self.parser = ParserX86ATT()
            start, end = self.find_marked_kernel_x86(parser_result)
        elif isa == 'AArch64':
            self.parser = ParserAArch64v81()
            start, end = self.find_marked_kernel_AArch64(parser_result)
        self.kernel = parser_result[start:end]

    def find_marked_kernel_AArch64(self, lines):
        nop_bytes = ['213', '3', '32', '31']
        return self.find_marked_kernel(lines, ['mov'], 'x1', [111, 222], nop_bytes)

    def find_marked_kernel_x86(self, lines):
        nop_bytes = ['100', '103', '144']
        return self.find_marked_kernel(lines, ['mov', 'movl'], 'ebx', [111, 222], nop_bytes)

    def find_marked_kernel(self, lines, mov_instr, mov_reg, mov_vals, nop_bytes):
        index_start = -1
        index_end = -1
        for i, line in enumerate(lines):
            if line['instruction'] in mov_instr and lines[i + 1]['directive'] is not None:
                source = line['operands']['source']
                destination = line['operands']['destination']
                # instruction pair matches, check for operands
                if (
                    'immediate' in source[0]
                    and self.parser.normalize_imd(source[0]['immediate']) == mov_vals[0]
                    and 'register' in destination[0]
                    and self.parser.get_full_reg_name(destination[0]['register']) == mov_reg
                ):
                    # operands of first instruction match start, check for second one
                    match, line_count = self.match_bytes(lines, i + 1, nop_bytes)
                    if(match):
                        # return first line after the marker
                        index_start = i + 1 + line_count
                elif (
                    'immediate' in source[0]
                    and self.parser.normalize_imd(source[0]['immediate']) == mov_vals[1]
                    and 'register' in destination[0]
                    and self.parser.get_full_reg_name(destination[0]['register']) == mov_reg
                ):
                    # operand of first instruction match end, check for second one
                    match, line_count = self.match_bytes(lines, i + 1, nop_bytes)
                    if(match):
                        # return line of the marker
                        index_end = i
            if index_start != -1 and index_end != -1:
                break
        return index_start, index_end

    def match_bytes(self, lines, index, byte_list):
        # either all bytes are in one line or in separate ones
        extracted_bytes = []
        line_count = 0
        while (
            index < len(lines)
            and lines[index]['directive'] is not None
            and lines[index]['directive']['name'] == 'byte'
        ):
            line_count += 1
            extracted_bytes += lines[index]['directive']['parameters']
            index += 1
        if extracted_bytes[0:len(byte_list)] == byte_list:
            return True, line_count
        return False, -1
