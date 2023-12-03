#!/usr/bin/env python3

from osaca.parser.operand import Operand


class MemoryOperand(Operand):
    def __init__(
        self,
        offset_ID=None,
        base_id=None,
        index_id=None,
        scale_id=1,
        segment_ext_id=None,
        mask=None,
        pre_indexed=False,
        post_indexed=False,
        indexed_val=None,
        port_pressure=[],
        dst=None,
        source=False,
        destination=False,
    ):
        super().__init__("memory", source, destination)
        self._offset_ID = offset_ID
        self._base_id = base_id
        self._index_id = index_id
        self._scale_id = scale_id
        self._segment_ext_id = segment_ext_id
        self._mask = mask
        self._pre_indexed = pre_indexed
        self._post_indexed = post_indexed
        self._indexed_val = indexed_val
        self._port_pressure = port_pressure
        self._dst = dst

    @property
    def offset(self):
        return self._offset_ID

    @property
    def immediate(self):
        return self._IMMEDIATE_ID

    @property
    def base(self):
        return self._base_id

    @property
    def index(self):
        return self._index_id

    @property
    def scale(self):
        return self._scale_id

    @property
    def segment_ext_id(self):
        return self._segment_ext_id

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
    def port_pressure(self):
        return self._port_pressure

    @property
    def dst(self):
        return self._dst

    @dst.setter
    def dst(self, dst):
        self._dst = dst

    @port_pressure.setter
    def port_pressure(self, port_pressure):
        self._port_pressure = port_pressure

    @segment_ext_id.setter
    def segment_ext_id(self, segment):
        self._segment_ext_id = segment

    @offset.setter
    def offset(self, offset):
        self._offset_ID = offset

    @base.setter
    def base(self, base):
        self._base_id = base

    @index.setter
    def index(self, index):
        self._index_id = index

    @scale.setter
    def scale(self, scale):
        self._scale_id = scale

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
            f"MemoryOperand(name={self._name}, offset_ID={self._offset_ID}, "
            f"base_id={self._base_id}, index_id={self._index_id}, scale_id={self._scale_id}, "
            f"segment_ext_id={self._segment_ext_id}, mask={self._mask}, "
            f"pre_indexed={self._pre_indexed}, post_indexed={self._post_indexed}, "
            f"indexed_val={self._indexed_val}, port_pressure={self._port_pressure}),"
            f"source={self._source}, destination={self._destination})"
        )

    def __repr__(self):
        return (
            f"MemoryOperand(name={self._name}, offset_ID={self._offset_ID}, "
            f"base_id={self._base_id}, index_id={self._index_id}, scale_id={self._scale_id}, "
            f"segment_ext_id={self._segment_ext_id}, mask={self._mask}, "
            f"pre_indexed={self._pre_indexed}, post_indexed={self._post_indexed}, "
            f"indexed_val={self._indexed_val}, port_pressure={self._port_pressure}),"
            f"source={self._source}, destination={self._destination})"
        )

    def __eq__(self, other):
        if isinstance(other, MemoryOperand):
            return (
                self._offset_ID == other._offset_ID
                and self._base_id == other._base_id
                and self._index_id == other._index_id
                and self._scale_id == other._scale_id
                and self._segment_ext_id == other._segment_ext_id
                and self._mask == other._mask
                and self._pre_indexed == other._pre_indexed
                and self._post_indexed == other._post_indexed
                and self._indexed_val == other._indexed_val
            )
        return False
