#!/usr/bin/env python3

from osaca.parser.operand import Operand


class IdentifierOperand(Operand):
    def __init__(self, name, OFFSET=None, RELOCATION=None):
        super().__init__(name)
        self._OFFSET = OFFSET
        self._RELOCATION = RELOCATION

    @property
    def offset(self):
        return self._OFFSET

    @offset.setter
    def offset(self, offset):
        self._OFFSET = offset

    @property
    def relocation(self):
        return self._RELOCATION

    @relocation.setter
    def relocation(self, relocation):
        self._RELOCATION = relocation

    def __str__(self):
        return (
            f"IdentifierOperand({self.name}, offset={self.offset}, relocation={self.relocation})"
        )

    def __repr__(self):
        return f"IdentifierOperand(name={self.name}, offset={self.offset}, relocation={self.relocation})"
