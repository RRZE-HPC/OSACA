#!/usr/bin/env python3

from osaca.parser.operand import Operand


class MemoryOperand(Operand):
    def __init__(
        self,
        OFFSET_ID=None,
        BASE_ID=None,
        INDEX_ID=None,
        SCALE_ID=1,
        SEGMENT_EXT_ID=None,
        MASK=None,
        PRE_INDEXED=False,
        POST_INDEXED=False,
        INDEXED_VAL=None,
    ):
        super().__init__("memory")
        self._OFFSET_ID = OFFSET_ID
        self._BASE_ID = BASE_ID
        self._INDEX_ID = INDEX_ID
        self._SCALE_ID = SCALE_ID
        self._SEGMENT_EXT_ID = SEGMENT_EXT_ID
        self._MASK = MASK
        self._PRE_INDEXED = PRE_INDEXED
        self._POST_INDEXED = POST_INDEXED
        self._INDEXED_VAL = INDEXED_VAL

    @property
    def offset(self):
        return self._OFFSET_ID

    @property
    def immediate(self):
        return self._IMMEDIATE_ID

    @property
    def base(self):
        return self._BASE_ID

    @property
    def index(self):
        return self._INDEX_ID

    @property
    def scale(self):
        return self._SCALE_ID

    @property
    def segment_ext_id(self):
        return self._SEGMENT_EXT_ID

    @property
    def mask(self):
        return self._MASK

    @property
    def pre_indexed(self):
        return self._PRE_INDEXED

    @property
    def post_indexed(self):
        return self._POST_INDEXED

    @property
    def indexed_val(self):
        return self._INDEXED_VAL

    @segment_ext_id.setter
    def segment_ext_id(self, segment):
        self._SEGMENT_EXT_ID = segment

    @offset.setter
    def offset(self, offset):
        self._OFFSET_ID = offset

    @base.setter
    def base(self, base):
        self._BASE_ID = base

    @index.setter
    def index(self, index):
        self._INDEX_ID = index

    @scale.setter
    def scale(self, scale):
        self._SCALE_ID = scale

    @mask.setter
    def mask(self, mask):
        self._MASK = mask

    @pre_indexed.setter
    def pre_indexed(self, pre_indexed):
        self._PRE_INDEXED = pre_indexed

    @post_indexed.setter
    def post_indexed(self, post_indexed):
        self._POST_INDEXED = post_indexed

    @indexed_val.setter
    def indexed_val(self, value):
        self._INDEXED_VAL = value

    def __str__(self):
        return (
            f"MemoryOperand(NAME_ID={self._NAME_ID}, OFFSET_ID={self._OFFSET_ID}, "
            f"BASE_ID={self._BASE_ID}, INDEX_ID={self._INDEX_ID}, SCALE_ID={self._SCALE_ID}, "
            f"SEGMENT_EXT_ID={self._SEGMENT_EXT_ID}, MASK={self._MASK}, "
            f"PRE_INDEXED={self._PRE_INDEXED}, POST_INDEXED={self._POST_INDEXED}, "
            f"INDEXED_VAL={self._INDEXED_VAL})"
        )

    def __repr__(self):
        return (
            f"MemoryOperand(NAME_ID={self._NAME_ID}, OFFSET_ID={self._OFFSET_ID}, "
            f"BASE_ID={self._BASE_ID}, INDEX_ID={self._INDEX_ID}, SCALE_ID={self._SCALE_ID}, "
            f"SEGMENT_EXT_ID={self._SEGMENT_EXT_ID}, MASK={self._MASK}, "
            f"PRE_INDEXED={self._PRE_INDEXED}, POST_INDEXED={self._POST_INDEXED}, "
            f"INDEXED_VAL={self._INDEXED_VAL})"
        )

    def __eq__(self, other):
        if isinstance(other, MemoryOperand):
            return (
                self._OFFSET_ID == other._OFFSET_ID
                and self._BASE_ID == other._BASE_ID
                and self._INDEX_ID == other._INDEX_ID
                and self._SCALE_ID == other._SCALE_ID
                and self._SEGMENT_EXT_ID == other._SEGMENT_EXT_ID
                and self._MASK == other._MASK
                and self._PRE_INDEXED == other._PRE_INDEXED
                and self._POST_INDEXED == other._POST_INDEXED
                and self._INDEXED_VAL == other._INDEXED_VAL
            )
        return False
