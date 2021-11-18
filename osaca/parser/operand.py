#!/usr/bin/env python3
"""Operand super class"""


class Operand:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Op({})".format(self.name)

    def is_dependent_of(self, operand):
        if isinstance(operand, Operand) and operand.name == self.name:
            return True
        return False
