#!/usr/bin/env python3
"""Register operand class"""

from osaca.parser import Operand


class IdentifierOperand(Operand):
    def __init__(self, name, offset=None, relocation=None):
        super().__init__(name)
        self.offset = offset
        self.relocation = relocation

    def __str__(self):
        return "{}{}".format(self.offset + "+" if self.offset else "", self.name)

    def __repr__(self):
        return "Id({}{})".format(self.offset + "+" if self.offset else "", self.name)

    def __eq__(self, other):
        if (
            self.name == other.name
            and self.offset == other.offset
            and self.relocation == other.relocation
        ):
            return True
        return False

    def is_dependent_of(self, operand):
        return False
