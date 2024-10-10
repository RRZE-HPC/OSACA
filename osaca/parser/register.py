#!/usr/bin/env python3

from osaca.parser.operand import Operand


class RegisterOperand(Operand):
    def __init__(
        self,
        name=None,
        width=None,
        prefix=None,
        regtype=None,
        lanes=None,
        shape=None,
        index=None,
        mask=False,
        zeroing=False,
        predication=None,
        source=False,
        destination=False,
        pre_indexed=False,
        post_indexed=False,
        shift=False,
        shift_op=False,
    ):
        super().__init__(source, destination)
        self._name = name
        self._width = width
        self._prefix = prefix.lower() if prefix else None
        self._regtype = regtype
        self._lanes = lanes
        self._shape = shape.lower() if shape else None
        self._index = index
        self._mask = mask
        self._zeroing = zeroing
        self._predication = predication.lower() if predication else None
        self._pre_indexed = pre_indexed
        self._post_indexed = post_indexed
        self._shift = shift
        self._shift_op = shift_op

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, shift):
        self._shift = shift

    @property
    def shift_op(self):
        return self._shift_op

    @shift_op.setter
    def shift_op(self, shift_op):
        self._shift_op = shift_op

    @property
    def predication(self):
        return self._predication

    @predication.setter
    def predication(self, predication):
        self._predication = predication

    @property
    def pre_indexed(self):
        return self._pre_indexed

    @property
    def post_indexed(self):
        return self._post_indexed

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix.lower()

    @property
    def regtype(self):
        return self._regtype

    @regtype.setter
    def regtype(self, regtype):
        self._regtype = regtype

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

    @pre_indexed.setter
    def pre_indexed(self, pre_indexed):
        self._pre_indexed = pre_indexed

    @post_indexed.setter
    def post_indexed(self, post_indexed):
        self._post_indexed = post_indexed

    @property
    def zeroing(self):
        return self._zeroing

    @zeroing.setter
    def zeroing(self, zeroing):
        self._zeroing = zeroing

    def __str__(self):
        return (
            f"Register(name={self._name}, width={self._width}, "
            f"prefix={self._prefix}, regtype={self._regtype}, "
            f"lanes={self._lanes}, shape={self._shape}, index={self._index}, "
            f"mask={self._mask}, zeroing={self._zeroing},source={self._source},destination={self._destination},"
            f"pre_indexed={self._pre_indexed}, post_indexed={self._post_indexed}) "
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, RegisterOperand):
            return (
                self._name == other._name
                and self._width == other._width
                and self._prefix == other._prefix
                and self._regtype == other._regtype
                and self._lanes == other._lanes
                and self._shape == other._shape
                and self._index == other._index
                and self._mask == other._mask
                and self._zeroing == other._zeroing
            )
        return False
