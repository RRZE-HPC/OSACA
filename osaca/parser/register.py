#!/usr/bin/env python3

from osaca.parser.operand import Operand


class RegisterOperand(Operand):
    def __init__(
        self,
        name_id=None,
        width_id=None,
        prefix_id=None,
        reg_id=None,
        regtype_id=None,
        lanes=None,
        shape=None,
        index=None,
        mask=False,
        zeroing=False,
        predication=None,
        source=False,
        destination=False,
    ):
        super().__init__(name_id, source, destination)
        self._width_id = width_id
        self._prefix_id = prefix_id
        self._reg_id = reg_id
        self._regtype_id = regtype_id
        self._lanes = lanes
        self._shape = shape
        self._index = index
        self._mask = mask
        self._zeroing = zeroing
        self._predication = predication

    @property
    def width(self):
        return self._width_id

    @width.setter
    def width(self, width):
        self._width_id = width

    @property
    def predication(self):
        return self._predication

    @predication.setter
    def predication(self, predication):
        self._predication = predication

    @property
    def regtype(self):
        return self._regtype_id

    @regtype.setter
    def regtype(self, regtype):
        self._regtype_id = regtype

    @property
    def prefix(self):
        return self._prefix_id

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix

    @property
    def reg_id(self):
        return self._reg_id

    @reg_id.setter
    def reg_id(self, reg_id):
        self._reg_id = reg_id

    @property
    def lanes(self):
        return self._lanes

    @lanes.setter
    def lanes(self, lanes):
        self._lanes = lanes

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        self._shape = shape

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        self._mask = mask

    @property
    def zeroing(self):
        return self._zeroing

    @zeroing.setter
    def zeroing(self, zeroing):
        self._zeroing = zeroing

    def __str__(self):
        return (
            f"RegisterOperand(name_id={self._name_id}, width_id={self._width_id}, "
            f"prefix_id={self._prefix_id}, reg_id={self._reg_id}, REGtype_id={self._regtype_id}, "
            f"lanes={self._lanes}, shape={self._shape}, index={self._index}, "
            f"mask={self._mask}, zeroing={self._zeroing})"
        )

    def __repr__(self):
        return (
            f"RegisterOperand(name_id={self._name_id}, width_id={self._width_id}, "
            f"prefix_id={self._prefix_id}, reg_id={self._reg_id}, REGtype_id={self._regtype_id}, "
            f"lanes={self._lanes}, shape={self._shape}, index={self._index}, "
            f"mask={self._mask}, zeroing={self._zeroing})"
        )

    def __eq__(self, other):
        if isinstance(other, RegisterOperand):
            return (
                self._name_id == other._name_id
                and self._width_id == other._width_id
                and self._prefix_id == other._prefix_id
                and self._reg_id == other._reg_id
                and self._regtype_id == other._regtype_id
                and self._lanes == other._lanes
                and self._shape == other._shape
                and self._index == other._index
                and self._mask == other._mask
                and self._zeroing == other._zeroing
            )
        return False
