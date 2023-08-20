#!/usr/bin/env python3

from osaca.parser.operand import Operand

class LabelOperand(Operand):
    def __init__(self, NAME_ID = None, COMMENT_ID = None):
        super().__init__()
        self._NAME_ID = NAME_ID
        self._COMMENT_ID = COMMENT_ID
    
    @property
    def name(self):
        return self._NAME_ID
    
    @name.setter
    def name(self, name):
        self._NAME_ID = name

    @property
    def comment(self):
        return self._COMMENT_ID
    
    @comment.setter
    def comment(self, comment):
        self._COMMENT_ID = comment
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self._COMMENT_ID:
            raise StopIteration
        return self._COMMENT_ID.pop(0)
    