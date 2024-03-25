#!/usr/bin/env python3

from osaca.parser.operand import Operand


class PrefetchOperand(Operand):
    def __init__(self, type_id=None, target=None, policy=None):
        self._type_id = type_id
        self._target = target
        self._policy = policy

    @property
    def type_id(self):
        return self._type_id

    @type_id.setter
    def type_id(self, type_id):
        self._type_id = type_id

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, policy):
        self._policy = policy

    def __str__(self):
        return f"Label(type_id={self._type_id},target={self._target},policy={self._policy})"

    def __repr__(self):
        return self.__str__()
