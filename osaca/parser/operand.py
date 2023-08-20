#!/usr/bin/env python3

class Operand:
    def __init__(self, NAME_ID):
        self._NAME_ID = NAME_ID

    @property
    def name(self):
        return self._NAME_ID

    @name.setter
    def name(self, name):
        self._NAME_ID = name
    
    def __repr__(self):
        return f"Operand(NAME_ID={self._NAME_ID}"

    def __str__(self):
        return f"Name: {self._NAME_ID}"