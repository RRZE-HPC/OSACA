#!/usr/bin/env python3

from osaca.parser.operand import Operand


class DirectiveOperand(Operand):
    def __init__(self, name=None, parameter_id=None, comment_id=None):
        super().__init__(name)
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
        if isinstance(other, DirectiveOperand):
            return (
                self._name == other._name
                and self._parameter_id == other._parameter_id
                and self._comment_id == other._comment_id
            )
        elif isinstance(other, dict):
            return self._name == other["name"] and self._parameter_id == other["parameters"]
        return False

    def __str__(self):
        return f"Directive(name={self._name}, parameters={self._parameter_id}, comment={self._comment_id})"

    def __repr__(self):
        return self.__str__()
