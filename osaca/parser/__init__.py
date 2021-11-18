"""
Collection of parsers supported by OSACA.

Only the parser below will be exported, so please add new parsers to __all__.
"""
from .attr_dict import AttrDict
from .base_parser import BaseParser
from .operand import Operand
from .directive_operand import DirectiveOperand
from .flag_operand import FlagOperand
from .identifier_operand import IdentifierOperand
from .immediate_operand import ImmediateOperand
from .mem_operand import MemoryOperand
from .prefetch_operand import PrefetchOperand
from .reg_operand import RegisterOperand
from .instruction import InstructionForm
from .parser_AArch64 import ParserAArch64
from .parser_x86att import ParserX86ATT

__all__ = [
    "AttrDict",
    "BaseParser",
    "ParserX86ATT",
    "ParserAArch64",
    "get_parser",
    "Operand",
    "DirectiveOperand",
    "FlagOperand",
    "IdentifierOperand",
    "ImmediateOperand",
    "MemoryOperand",
    "PrefetchOperand",
    "RegisterOperand",
    "InstructionForm"
]


def get_parser(isa):
    if isa.lower() == "x86":
        return ParserX86ATT()
    elif isa.lower() == "aarch64":
        return ParserAArch64()
    else:
        raise ValueError("Unknown ISA {!r}.".format(isa))
