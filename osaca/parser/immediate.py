#!/usr/bin/env python3

from osaca.parser.operand import Operand


class ImmediateOperand(Operand):
    def __init__(
        self,
        IDENTIFIER_ID=None,
        TYPE_ID=None,
        VALUE_ID=None,
        SHIFT_ID=None,
        SOURCE=False,
        DESTINATION=False
    ):
        super().__init__(str(VALUE_ID))
        self._IDENTIFIER_ID = IDENTIFIER_ID
        self._TYPE_ID = TYPE_ID
        self._VALUE_ID = VALUE_ID
        self._SHIFT_ID = SHIFT_ID
        self._SOURCE = SOURCE
        self._DESTINATION = DESTINATION

    @property
    def identifier(self):
        return self._IDENTIFIER_ID

    @property
    def type(self):
        return self._TYPE_ID

    @property
    def value(self):
        return self._VALUE_ID

    @property
    def shift(self):
        return self._TYPE_ID

    @property
    def source(self):
        return self._SOURCE

    @source.setter
    def source(self, source):
        self._SOURCE = source

    @property
    def destination(self):
        return self._DESTINATION

    @destination.setter
    def destination(self, destination):
        self._DESTINATION = destination

    @identifier.setter
    def identifier(self, identifier):
        self._IDENTIFIER_ID = identifier

    @type.setter
    def type(self, type):
        self._TYPE_ID = type

    @value.setter
    def value(self, value):
        self._VALUE_ID = value

    @shift.setter
    def index(self, shift):
        self._SHIFT_ID = shift

    def __str__(self):
        return (
            f"ImmediateOperand(IDENTIFIER_ID={self._IDENTIFIER_ID}, TYPE_ID={self._TYPE_ID}, "
            f"VALUE_ID={self._VALUE_ID}, SHIFT_ID={self._SHIFT_ID})"
        )

    def __repr__(self):
        return (
            f"ImmediateOperand(IDENTIFIER_ID={self._IDENTIFIER_ID}, TYPE_ID={self._TYPE_ID}, "
            f"VALUE_ID={self._VALUE_ID}, SHIFT_ID={self._SHIFT_ID})"
        )

    def __eq__(self, other):
        if isinstance(other, ImmediateOperand):
            return (
                self._IDENTIFIER_ID == other._IDENTIFIER_ID
                and self._TYPE_ID == other._TYPE_ID
                and self._VALUE_ID == other._VALUE_ID
                and self._SHIFT_ID == other._SHIFT_ID
            )
        return False
