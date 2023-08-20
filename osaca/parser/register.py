#!/usr/bin/env python3

from osaca.parser.operand import Operand

class RegisterOperand(Operand):
    def __init__(self, NAME_ID = None, WIDTH_ID = None, PREFIX_ID = None, REG_ID = None
    , REGTYPE_ID = None, LANES = None, SHAPE = None, INDEX = False
    , MASK = False, ZEROING = False):
        super().__init__(NAME_ID)
        self._WIDTH_ID = WIDTH_ID
        self._PREFIX_ID = PREFIX_ID
        self._REG_ID = REG_ID
        self._LANES = LANES
        self._SHAPE = SHAPE
        self._INDEX = INDEX
        self._MASK = MASK
        self._ZEROING = ZEROING

    @property
    def width(self):
        return self._WIDTH_ID
    
    @width.setter
    def width(self, width):
        self._WIDTH_ID = width
    
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

    def __str__(self):
        return f"MemoryOperand({self.width_id}, {self.prefix_id}, {self.reg_id}, {self.lanes}, {self.shape}, {self.index}, {self.mask}, {self.zeroing})"
    
    def __repr__(self):
        return f"MemoryOperand(width_id={self.width_id}, prefix_id={self.prefix_id}, reg_id={self.reg_id}, lanes={self.lanes}, shape={self.shape}, index={self.index}, mask={self.mask}, zeroing={self.zeroing})"