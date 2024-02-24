#!/usr/bin/env python3

from osaca.parser.operand import Operand


class ConditionOperand(Operand):
    def __init__(
        self,
        ccode=None,
        source=False,
        destination=False,
    ):
        super().__init__(source, destination)
        self._ccode = ccode

    @property
    def ccode(self):
        return self._ccode

    @ccode.setter
    def ccode(self, ccode):
        self._ccode = ccode

    def __str__(self):
        return f"Condition(ccode={self._ccode}, source={self._source}, destination={self._destination})"

    def __repr__(self):
        return self.__str__()
