#!/usr/bin/env python3

from osaca.parser.operand import Operand


class FlagOperand(Operand):
    def __init__(self, name=None, source=False, destination=False):
        self._name = name
        super().__init__(source, destination)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __str__(self):
        return f"Flag(name={self._name}, source={self._source}, relocation={self._destination})"

    def __repr__(self):
        return self.__str__()
