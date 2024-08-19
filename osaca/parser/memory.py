#!/usr/bin/env python3

from osaca.parser.operand import Operand


class MemoryOperand(Operand):
    def __init__(
        self,
        offset=None,
        base=None,
        index=None,
        scale=1,
        segment_ext=None,
        mask=None,
        pre_indexed=False,
        post_indexed=False,
        indexed_val=None,
        src=None,
        dst=None,
        source=False,
        destination=False,
    ):
        super().__init__(source, destination)
        self._offset = offset
        self._base = base
        self._index = index
        self._scale = scale
        self._segment_ext = segment_ext
        self._mask = mask
        self._pre_indexed = pre_indexed
        self._post_indexed = post_indexed
        self._indexed_val = indexed_val
        # type of register we store from (`src`) or load to (`dst`)
        self._src = src
        self._dst = dst

    @property
    def offset(self):
        return self._offset

    @property
    def immediate(self):
        return self._immediate_id

    @property
    def base(self):
        return self._base

    @property
    def index(self):
        return self._index

    @property
    def scale(self):
        return self._scale

    @property
    def segment_ext(self):
        return self._segment_ext

    @property
    def mask(self):
        return self._mask

    @property
    def pre_indexed(self):
        return self._pre_indexed

    @property
    def post_indexed(self):
        return self._post_indexed

    @property
    def indexed_val(self):
        return self._indexed_val

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, src):
        self._src = src

    @property
    def dst(self):
        return self._dst

    @dst.setter
    def dst(self, dst):
        self._dst = dst

    @segment_ext.setter
    def segment_ext(self, segment):
        self._segment_ext = segment

    @offset.setter
    def offset(self, offset):
        self._offset = offset

    @base.setter
    def base(self, base):
        self._base = base

    @index.setter
    def index(self, index):
        self._index = index

    @scale.setter
    def scale(self, scale):
        self._scale = scale

    @mask.setter
    def mask(self, mask):
        self._mask = mask

    @pre_indexed.setter
    def pre_indexed(self, pre_indexed):
        self._pre_indexed = pre_indexed

    @post_indexed.setter
    def post_indexed(self, post_indexed):
        self._post_indexed = post_indexed

    @indexed_val.setter
    def indexed_val(self, value):
        self._indexed_val = value

    def __str__(self):
        return (
            f"MemoryOperand(offset={self._offset}, "
            f"base={self._base}, index={self._index}, scale={self._scale}, "
            f"segment_ext={self._segment_ext}, mask={self._mask}, "
            f"pre_indexed={self._pre_indexed}, post_indexed={self._post_indexed}, "
            f"indexed_val={self._indexed_val},"
            f"source={self._source}, destination={self._destination})"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, MemoryOperand):
            return (
                self._offset == other._offset
                and self._base == other._base
                and self._index == other._index
                and self._scale == other._scale
                and self._segment_ext == other._segment_ext
                and self._mask == other._mask
                and self._pre_indexed == other._pre_indexed
                and self._post_indexed == other._post_indexed
                and self._indexed_val == other._indexed_val
            )
        return False
