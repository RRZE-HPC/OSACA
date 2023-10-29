#!/usr/bin/env python3

from osaca.parser.operand import Operand


class directiveOperand(Operand):
    def __init__(self, name_id=None, parameter_id=None, comment_id=None):
        super().__init__(name_id)
        self._parameter_id = parameter_id
        self._comment_id = comment_id

    @property
    def parameters(self):
        return self._parameter_id

    @property
    def comment(self):
        return self._comment_id

    def __iter__(self):
        return self

    def __next__(self):
        if not self._comment_id:
            raise StopIteration
        return self._comment_id.pop(0)

    @parameters.setter
    def parameters(self, parameters):
        self._parameter_id = parameters

    @comment.setter
    def comment(self, comment):
        self._comment_id = comment

    def __eq__(self, other):
        if isinstance(other, directiveOperand):
            return (
                self._name_id == other._name_id
                and self._parameter_id == other._parameter_id
                and self._comment_id == other._comment_id
            )
        elif isinstance(other, dict):
            return self._name_id == other["name"] and self._parameter_id == other["parameters"]
        return False

    def __str__(self):
        return f"Directive(name_id={self._name_id}, parameters={self._parameter_id}, comment={self._comment_id})"

    def __repr__(self):
        return f"directiveOperand(name_id={self._name_id}, parameters={self._parameter_id}, comment={self._comment_id})"
