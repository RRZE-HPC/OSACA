#!/usr/bin/env python3

from osaca.parser.operand import Operand


class LabelOperand(Operand):
    def __init__(self, name=None):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __str__(self):
        return f"Label(name={self._name}"

    def __repr__(self):
        return self.__str__()
