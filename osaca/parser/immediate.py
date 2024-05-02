#!/usr/bin/env python3

from osaca.parser.operand import Operand


class ImmediateOperand(Operand):
    def __init__(
        self,
        identifier=None,
        imd_type=None,
        value=None,
        shift=None,
        source=False,
        destination=False,
    ):
        super().__init__(source, destination)
        self._identifier = identifier
        self._imd_type = imd_type
        self._value = value
        self._shift = shift

    @property
    def identifier(self):
        return self._identifier

    @property
    def imd_type(self):
        return self._imd_type

    @property
    def value(self):
        return self._value

    @property
    def shift(self):
        return self._imd_type

    @imd_type.setter
    def imd_type(self, itype):
        self._imd_type = itype

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier

    @value.setter
    def value(self, value):
        self._value = value

    @shift.setter
    def shift(self, shift):
        self._shift = shift

    def __str__(self):
        return (
            f"Immediate(identifier={self._identifier}, imd_type={self._imd_type}, "
            f"value={self._value}, shift={self._shift}, source={self._source}, destination={self._destination})"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, ImmediateOperand):
            return (
                self._identifier == other._identifier
                and self._imd_type == other._imd_type
                and self._value == other._value
                and self._shift == other._shift
            )
        return False
