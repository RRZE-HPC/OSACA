#!/usr/bin/env python3
"""Flag operand class"""

from osaca.parser import Operand

FLAGS_X86 = [
    "CF",
    "PF",
    "AF",
    "ZF",
    "SF",
    "TF",
    "IF",
    "DF",
    "OF",
    "IOPL",
    "NT",
    "RF",
    "VM",
    "AC",
    "VIF",
    "VIP",
    "ID",
]
FLAGS_AARCH64 = ["N", "Z", "C", "V"]


class FlagOperand(Operand):
    def __init__(self, name):
        super().__init__(str(name).upper())

    def __str__(self):
        return self.name

    def __repr__(self):
        return "FlagOp({})".format(self.name)

    def is_dependent_of(self, operand):
        if isinstance(operand, FlagOperand) and operand.name == self.name:
            return True
        return False
