#!/usr/bin/env python3

from osaca.parser.operand import Operand

class DirectiveOperand(Operand):
    def __init__(self, NAME_ID = None, PARAMETER_ID = None, COMMENT_ID = None):
        super().__init__(NAME_ID)
        self._PARAMETER_ID = PARAMETER_ID
        self._COMMENT_ID = COMMENT_ID
    
    @property
    def parameters(self):
        return self._PARAMETER_ID
    
    @property
    def comment(self):
        return self._COMMENT_ID

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self._COMMENT_ID:
            raise StopIteration
        return self._COMMENT_ID.pop(0)

    @parameters.setter
    def parameters(self, parameters):
        self._PARAMETER_ID = parameters
    
    @comment.setter
    def comment(self, comment):
        self._COMMENT_ID = comment
        
    def __eq__(self, other):
        if isinstance(other, DirectiveOperand):
            return (
                self._NAME_ID == other._NAME_ID and
                self._PARAMETER_ID == other._PARAMETER_ID and
                self._COMMENT_ID == other._COMMENT_ID
            )
        return False

    def __str__(self):
        return f"Directive(NAME_ID={self._NAME_ID}, PARAMETERS={self._PARAMETER_ID}, COMMENT={self._COMMENT_ID})"

    def __repr__(self):
        return f"DirectiveOperand(NAME_ID={self._NAME_ID}, PARAMETERS={self._PARAMETER_ID}, COMMENT={self._COMMENT_ID})"