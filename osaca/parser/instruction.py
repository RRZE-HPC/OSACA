#!/usr/bin/env python3
"""Instruction class"""


class InstructionForm:
    def __init__(
        self,
        line,
        mnemonic=None,
        operands=[],
        comment=None,
        directive=None,
        label=None,
        line_number=None,
    ):
        self.line = line
        self.mnemonic = mnemonic.upper() if mnemonic is not None else mnemonic
        self.operands = [o for o in operands]
        self.comment = comment
        self.directive = directive
        self.label = label
        self.line_number = line_number

        self.uops = None
        self.semantic_operands = {"source": [], "destination": [], "src_dst": []}
        self.latency = None
        self.throughput = None
        self.latency_cp = []
        self.latency_lcd = []
        self.latency_wo_load = None
        self.port_pressure = []
        self.port_uops = []
        self.flags = []

    def __str__(self):
        return self.line

    def __repr__(self):
        return str(self.__dict__)
