#!/usr/bin/env python3

from osaca.parser.operand import Operand


class RegisterOperand(Operand):
    def __init__(
        self,
        NAME_ID=None,
        WIDTH_ID=None,
        PREFIX_ID=None,
        REG_ID=None,
        REGTYPE_ID=None,
        LANES=None,
        SHAPE=None,
        INDEX=None,
        MASK=False,
        ZEROING=False,
        PREDICATION=None,
        SOURCE=False,
        DESTINATION=False,
    ):
        super().__init__(NAME_ID)
        self._WIDTH_ID = WIDTH_ID
        self._PREFIX_ID = PREFIX_ID
        self._REG_ID = REG_ID
        self._REGTYPE_ID = REGTYPE_ID
        self._LANES = LANES
        self._SHAPE = SHAPE
        self._INDEX = INDEX
        self._MASK = MASK
        self._ZEROING = ZEROING
        self._PREDICATION = PREDICATION
        self._SOURCE = SOURCE
        self._DESTINATION = DESTINATION

    @property
    def width(self):
        return self._WIDTH_ID

    @width.setter
    def width(self, width):
        self._WIDTH_ID = width

    @property
    def predication(self):
        return self._PREDICATION

    @predication.setter
    def predication(self, predication):
        self._PREDICATION = predication

    @property
    def regtype(self):
        return self._REGTYPE_ID

    @regtype.setter
    def regtype(self, regtype):
        self._REGTYPE_ID = regtype

    @property
    def prefix(self):
        return self._PREFIX_ID

    @prefix.setter
    def prefix(self, prefix):
        self._PREFIX = prefix

    @property
    def reg_id(self):
        return self._REG_ID

    @reg_id.setter
    def reg_id(self, reg_id):
        self._REG_ID = reg_id

    @property
    def lanes(self):
        return self._LANES

    @lanes.setter
    def lanes(self, lanes):
        self._LANES = lanes

    @property
    def shape(self):
        return self._SHAPE

    @shape.setter
    def shape(self, shape):
        self._SHAPE = shape

    @property
    def index(self):
        return self._INDEX

    @index.setter
    def index(self, index):
        self._INDEX = index

    @property
    def mask(self):
        return self._MASK

    @mask.setter
    def mask(self, mask):
        self._MASK = mask

    @property
    def zeroing(self):
        return self._ZEROING

    @zeroing.setter
    def zeroing(self, zeroing):
        self._ZEROING = zeroing

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

    def __str__(self):
        return (
            f"RegisterOperand(NAME_ID={self._NAME_ID}, WIDTH_ID={self._WIDTH_ID}, "
            f"PREFIX_ID={self._PREFIX_ID}, REG_ID={self._REG_ID}, REGTYPE_ID={self._REGTYPE_ID}, "
            f"LANES={self._LANES}, SHAPE={self._SHAPE}, INDEX={self._INDEX}, "
            f"MASK={self._MASK}, ZEROING={self._ZEROING}),"
            f"SOURCE={self._SOURCE}, DESTINATION={self._DESTINATION})"
        )

    def __repr__(self):
        return (
            f"RegisterOperand(NAME_ID={self._NAME_ID}, WIDTH_ID={self._WIDTH_ID}, "
            f"PREFIX_ID={self._PREFIX_ID}, REG_ID={self._REG_ID}, REGTYPE_ID={self._REGTYPE_ID}, "
            f"LANES={self._LANES}, SHAPE={self._SHAPE}, INDEX={self._INDEX}, "
            f"MASK={self._MASK}, ZEROING={self._ZEROING}),"
            f"SOURCE={self._SOURCE}, DESTINATION={self._DESTINATION})"
        )

    def __eq__(self, other):
        if isinstance(other, RegisterOperand):
            return (
                self._NAME_ID == other._NAME_ID
                and self._WIDTH_ID == other._WIDTH_ID
                and self._PREFIX_ID == other._PREFIX_ID
                and self._REG_ID == other._REG_ID
                and self._REGTYPE_ID == other._REGTYPE_ID
                and self._LANES == other._LANES
                and self._SHAPE == other._SHAPE
                and self._INDEX == other._INDEX
                and self._MASK == other._MASK
                and self._ZEROING == other._ZEROING
            )
        return False
