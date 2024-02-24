#!/usr/bin/env python3

from osaca.parser.operand import Operand


class DirectiveOperand(Operand):
    def __init__(self, name=None, parameter_id=None):
        super().__init__(name)
        self._parameter_id = parameter_id

    @property
    def parameters(self):
        return self._parameter_id

    @parameters.setter
    def parameters(self, parameters):
        self._parameter_id = parameters


    def __eq__(self, other):
        if isinstance(other, DirectiveOperand):
            return (
                self._name == other._name
                and self._parameter_id == other._parameter_id
            )
        elif isinstance(other, dict):
            return self._name == other["name"] and self._parameter_id == other["parameters"]
        return False

    def __str__(self):
        return f"Directive(name={self._name}, parameters={self._parameter_id})"

    def __repr__(self):
        return self.__str__()
