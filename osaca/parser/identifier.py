#!/usr/bin/env python3

from osaca.parser.operand import Operand


class IdentifierOperand(Operand):
    def __init__(self, name=None, offset=None, relocation=None):
        super().__init__(name)
        self._offset = offset
        self._relocation = relocation

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        self._offset = offset

    @property
    def relocation(self):
        return self._relocation

    @relocation.setter
    def relocation(self, relocation):
        self._relocation = relocation

    def __str__(self):
        return (
            f"IdentifierOperand({self.name}, offset={self.offset}, relocation={self.relocation})"
        )

    def __repr__(self):
        return f"IdentifierOperand(name={self.name}, offset={self.offset}, relocation={self.relocation})"
