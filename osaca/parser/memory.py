#!/usr/bin/env python3

from osaca.parser.operand import Operand

class MemoryOperand(Operand):
    def __init__(self, OFFSET_ID = None, BASE_ID = None, INDEX_ID = None
    , SCALE_ID = None, SEGMENT_EXT_ID = None, MASK = None, PRE_INDEXED = False
    , POST_INDEXED = False, IMMEDIATE_ID = None):
        super().__init__()
        self._OFFSET_ID = OFFSET_ID
        self._BASE_ID = BASE_ID
        self._INDEX_ID = INDEX_ID
        self._SCALE_ID = SCALE_ID
        self._SEGMENT_EXT_ID = SEGMENT_EXT_ID
        self._MASK = MASK 
        self._PRE_INDEXED = PRE_INDEXED
        self._POST_INDEXED = POST_INDEXED
        self._IMMEDIATE_ID = IMMEDIATE_ID  

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
    
    @segment_ext_id.setter
    def segment_ext_id(self, segment):
        self._SEGMENT_EXT_ID= segment  

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