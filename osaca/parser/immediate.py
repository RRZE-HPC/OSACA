#!/usr/bin/env python3

from osaca.parser.operand import Operand

class ImmediateOperand(Operand):
    def __init__(self, IDENTIFIER_ID = None, TYPE_ID = None, VALUE_ID = None, SHIFT_ID = None
    , ):
        super().__init__()
        self._IDENTIFIER_ID = IDENTIFIER_ID
        self._TYPE_ID = TYPE_ID
        self._VALUE_ID = VALUE_ID
        self._SHIFT_ID = SHIFT_ID

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

