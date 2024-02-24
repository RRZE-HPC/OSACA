#!/usr/bin/env python3

from osaca.parser.operand import Operand


class LabelOperand(Operand):
    def __init__(self, name=None):
        super().__init__(name)

    def __str__(self):
        return f"Label(name={self._name}"

    def __repr__(self):
        return self.__str__()
