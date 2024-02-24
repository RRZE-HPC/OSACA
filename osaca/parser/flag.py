#!/usr/bin/env python3

from osaca.parser.operand import Operand


class FlagOperand(Operand):
    def __init__(self, name=None, source=False, destination=False):
        super().__init__(name, source, destination)

    def __str__(self):
        return (
            f"Flag(name={self._name}, source={self._source}, relocation={self._destination})"
        )

    def __repr__(self):
        return self.__str__()
