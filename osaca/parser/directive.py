#!/usr/bin/env python3

from osaca.parser.operand import Operand


class DirectiveOperand(Operand):
    def __init__(self, name=None, parameters=None):
        self._name = name
        self._parameters = parameters

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        self._parameters = parameters

    def __eq__(self, other):
        if isinstance(other, DirectiveOperand):
            return self._name == other._name and self._parameters == other._parameters
        elif isinstance(other, dict):
            return self._name == other["name"] and self._parameters == other["parameters"]
        return False

    def __str__(self):
        return f"Directive(name={self._name}, parameters={self._parameters})"

    def __repr__(self):
        return self.__str__()
