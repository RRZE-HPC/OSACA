#!/usr/bin/env python3
"""Memory operand class"""

from osaca.parser import Operand
import osaca.parser.reg_operand as RegisterOperand


class MemoryOperand(Operand):
    def __init__(
        self,
        name,
        offset=None,
        base=None,
        index=None,
        scale=1,
        mask=None,
        segm_ext=None,
        pre_indexed=False,
        post_indexed=False,
        indexed_val=None
    ):
        super().__init__(name)
        self.offset = offset
        self.base = base
        self.index = index
        self.scale = scale
        self.mask = mask
        self.segment_extension = segm_ext
        self.pre_indexed = pre_indexed
        self.post_indexed = post_indexed
        self.indexed_val = indexed_val

    def __str__(self):
        return self.name

    def __repr__(self):
        offs_str = " " if not self.offset or self.post_indexed else repr(self.offset)
        base_str = " " if not self.base else repr(self.base)
        index_str = "" if not self.index else ", {}".format(repr(self.index))
        scale_str = "" if self.scale == 1 else ", {}".format(self.scale)
        mask_str = "" if not self.mask else "{{{}}}".format(repr(self.mask))
        indexed_str = "" if not self.post_indexed or self.pre_indexed else ", {}".format(repr(self.indexed_val))
        indexed_str += "!" if self.pre_indexed else ""
        return "Mem({}({}{}{}){}{}{})".format(
            offs_str,
            base_str,
            index_str,
            scale_str,
            "!" if self.pre_indexed else "",
            mask_str,
            indexed_str,
        )

    def is_dependent_of(self, operand):
        if not isinstance(operand, RegisterOperand) or not isinstance(operand, MemoryOperand):
            return False
        used_regs = [op for op in [self.offset, self.base, self.index, self.mask] if op is not None]
        if isinstance(operand, RegisterOperand):
            # RegisterOperand
            if any([reg.is_dependent_of(operand) for reg in used_regs]):
                return True
            return False
        else:
            # MemoryOperand
            if operand.pre_indexed or operand.post_indexed:
                if any([reg.is_dependent_of(operand.base) for reg in used_regs]):
                    return True
            return False
