#!/usr/bin/env python3
"""Directive operand class"""

from osaca.parser import Operand


class DirectiveOperand(Operand):
    def __init__(self, name, directive, parameters):
        super().__init__(name)
        self.directive = directive
        self.parameters = parameters

    def __eq__(self, other):
        if self.directive == other.directive:
            for par in self.parameters:
                if par not in other.parameters:
                    return False
            return True
        return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Dir({} | {})".format(self.directive, ", ".join([param for param in self.parameters]))

    def is_dependent_of(self, operand):
        return False
