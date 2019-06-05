#!/usr/bin/env python3

from osaca.parser import ParserAArch64v81, ParserX86ATT
# from .marker_utils import reduce_to_section


class Analyzer(object):
    def __init__(self, parser_result, isa):
        self.ISA = isa
        if isa == 'x86':
            self.parser = ParserX86ATT()
        elif isa == 'AArch64':
            self.parser = ParserAArch64v81()
        self.kernel = parser_result
