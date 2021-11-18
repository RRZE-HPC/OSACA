#!/usr/bin/env python3
"""Register operand class"""

from osaca.parser import Operand


class IdentifierOperand(Operand):
    def __init__(self, name, offset=None):
        super().__init__(name)
        self.offset = offset

    def __str__(self):
        return "{}{}".format(self.offset + "+" if self.offset else "", self.name)

    def __repr__(self):
        return "Id({}{})".format(self.offset + "+" if self.offset else "", self.name)

    def is_dependent_of(self, operand):
        return False
