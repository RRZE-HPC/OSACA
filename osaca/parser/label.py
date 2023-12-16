#!/usr/bin/env python3

from osaca.parser.operand import Operand


class LabelOperand(Operand):
    def __init__(self, name=None, comment_id=None):
        super().__init__(name)
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
        return f"Label(name={self._name}, comment={self._comment_id})"

    def __repr__(self):
        return self.__str__()
