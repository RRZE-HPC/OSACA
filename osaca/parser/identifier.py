#!/usr/bin/env python3

from osaca.parser.operand import Operand


class IdentifierOperand(Operand):
    def __init__(self, name=None, offset=None, relocation=None, source=False, destination=False):
        super().__init__(source, destination)
        self._name = name
        self._offset = offset
        self._relocation = relocation

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def offset(self):
        return self._offset

    @property
    def relocation(self):
        return self._relocation

    @offset.setter
    def offset(self, offset):
        self._offset = offset

    @relocation.setter
    def relocation(self, relocation):
        self._relocation = relocation

    def __str__(self):
        return (
            f"Identifier(name={self._name}, offset={self._offset}, relocation={self._relocation})"
        )

    def __repr__(self):
        return self.__str__()
