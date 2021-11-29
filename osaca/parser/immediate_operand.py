#!/usr/bin/env python3
"""Immediate operand class"""

from osaca.parser import Operand


class ImmediateOperand(Operand):
    def __init__(self, value):
        super().__init__(str(value))
        self.value = self.conv2decimal(value)
        self.itype = "int" if int(self.value) == self.value else "float"

    def __eq__(self, other):
        if not isinstance(other, ImmediateOperand):
            return False
        return self.value == other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Imd({})".format(self.value)

    def conv2decimal(self, value):
        try:
            return int(value, 0)
        except (ValueError, TypeError):
            # check for float
            try:
                tmp_val = float(value)
                if tmp_val == int(tmp_val):
                    return int(tmp_val)
                else:
                    return tmp_val
            except ValueError:
                raise ValueError("Could not convert given value {} to a valid immediate.".format(value))

    def is_dependent_of(self, operand):
        return False
