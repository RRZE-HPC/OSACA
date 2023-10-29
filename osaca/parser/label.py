#!/usr/bin/env python3

from osaca.parser.operand import Operand


class labelOperand(Operand):
    def __init__(self, name_id=None, comment_id=None):
        super().__init__(name_id)
        self._comment_id = comment_id

    @property
    def comment(self):
        return self._comment_id

    @comment.setter
    def comment(self, comment):
        self._comment_id = comment

    def __iter__(self):
        return self

    def __next__(self):
        if not self._comment_id:
            raise StopIteration
        return self._comment_id.pop(0)

    def __str__(self):
        return f"labelOperand(name_id={self._name_id}, comment={self._comment_id})"

    def __repr__(self):
        return f"labelOperand(name_id={self._name_id}, comment={self._comment_id})"
