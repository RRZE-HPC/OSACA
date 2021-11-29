#!/usr/bin/env python3
"""Register operand class"""

import osaca.parser.mem_operand as MemoryOperand
from osaca.parser import Operand


class RegisterOperand(Operand):
    def __init__(
        self,
        name,
        width=None,
        prefix=None,
        regid=None,
        regtype=None,
        lanes=None,
        shape=None,
        index=None,
        mask=None,
        zeroing=False,
    ):
        super().__init__(name)
        self.width = width
        self.prefix = prefix
        self.regid = regid
        self.regtype = regtype
        self.lanes = lanes
        self.shape = shape
        self.index = index
        self.mask = mask
        self.zeroing = zeroing

    def __str__(self):
        return self.name

    def __repr__(self):
        add_str = ", "
        if self.lanes and self.shape:
            add_str += ".{}{}".format(self.lanes, self.shape)
        else:
            add_str += ".{}".format(self.shape) if self.shape else ""
        add_str += "[{}]".format(self.index) if self.index else ""
        add_str += "{{{}}}".format(repr(self.mask)) if self.mask else ""
        add_str += "{z}" if self.zeroing else ""
        if add_str == ", ":
            add_str = ""
        return "Reg({}, {}, {}b, {}{})".format(
            self.prefix, self.regid, self.width, self.regtype, add_str
        )

    def __eq__(self, other):
        if (
            self.prefix.lower() == other.prefix.lower()
            and self.regid.lower() == other.regid.lower()
            and self.regtype == other.regtype
            and self.shape == other.shape
            and (any(te.lanes is None for te in [self, other]) or self.lanes == other.lanes)
            and (any(te.index is None for te in [self, other]) or self.index == other.index)
            and (any(te.mask is None for te in [self, other]) or self.mask == other.mask)
        ):
            return True
        return False

    def is_dependent_of(self, operand):
        if not isinstance(operand, RegisterOperand) or not isinstance(operand, MemoryOperand):
            return False
        if isinstance(operand, RegisterOperand):
            # RegisterOperand
            if self.regtype == operand.regtype and self.regid == operand.regid:
                return True
            return False
        else:
            # MemoryOperand
            if operand.pre_indexed or operand.post_indexed:
                if self.is_dependent_of(operand.prefix):
                    return True
            return False
