#!/usr/bin/env python3
"""Immediate operand class"""

from osaca.parser import Operand


class PrefetchOperand(Operand):
    def __init__(self, ptype, target, policy):
        super().__init__(str(ptype).lower() + str(target).lower() + str(policy).lower())
        self.ptype = ptype
        self.target = target
        self.policy = policy

    def __eq__(self, other):
        return self.ptype.lower() == other.ptype.lower() and self.target.lower() == other.target.lower() and self.policy.lower() == other.policy.lower()

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return "PrfOp({}, {}, {})".format(self.ptype, self.target, self.policy)
