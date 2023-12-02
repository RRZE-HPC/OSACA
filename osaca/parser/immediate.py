#!/usr/bin/env python3

from osaca.parser.operand import Operand


class ImmediateOperand(Operand):
    def __init__(
        self,
        identifier_id=None,
        type_id=None,
        value_id=None,
        shift_id=None,
        source=False,
        destination=False,
    ):
        super().__init__(str(value_id), source, destination)
        self._identifier_id = identifier_id
        self._type_id = type_id
        self._value_id = value_id
        self._shift_id = shift_id

    @property
    def identifier(self):
        return self._identifier_id

    @property
    def type(self):
        return self._type_id

    @property
    def value(self):
        return self._value_id

    @property
    def shift(self):
        return self._type_id

    @identifier.setter
    def identifier(self, identifier):
        self._identifier_id = identifier

    @type.setter
    def type(self, type):
        self._type_id = type

    @value.setter
    def value(self, value):
        self._value_id = value

    @shift.setter
    def index(self, shift):
        self._shift_id = shift

    def __str__(self):
        return (
            f"ImmediateOperand(identifier_id={self._identifier_id}, type_id={self._type_id}, "
            f"value_id={self._value_id}, shift_id={self._shift_id}, source={self._source}, destination={self._destination})"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, ImmediateOperand):
            return (
                self._identifier_id == other._identifier_id
                and self._type_id == other._type_id
                and self._value_id == other._value_id
                and self._shift_id == other._shift_id
            )
        return False
