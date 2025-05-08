import re
import string

from osaca.parser import BaseParser


class ParserX86(BaseParser):
    _instance = None

    # Singleton pattern, as this is created very many times.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParserX86, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    def isa(self):
        return "x86"

    def is_reg_dependend_of(self, reg_a, reg_b):
        """Check if ``reg_a`` is dependent on ``reg_b``"""
        reg_a_name = reg_a.name.upper()
        reg_b_name = reg_b.name.upper()

        # Check if they are the same registers
        if reg_a_name == reg_b_name:
            return True
        # Check vector registers first
        if self.is_vector_register(reg_a):
            if self.is_vector_register(reg_b):
                if reg_a_name[1:] == reg_b_name[1:]:
                    # Registers in the same vector space
                    return True
            return False
        # Check basic GPRs
        gpr_groups = {
            "A": ["RAX", "EAX", "AX", "AH", "AL"],
            "B": ["RBX", "EBX", "BX", "BH", "BL"],
            "C": ["RCX", "ECX", "CX", "CH", "CL"],
            "D": ["RDX", "EDX", "DX", "DH", "DL"],
            "SP": ["RSP", "ESP", "SP", "SPL"],
            "SRC": ["RSI", "ESI", "SI", "SIL"],
            "DST": ["RDI", "EDI", "DI", "DIL"],
        }
        if self.is_basic_gpr(reg_a):
            if self.is_basic_gpr(reg_b):
                for dep_group in gpr_groups.values():
                    if reg_a_name in dep_group:
                        if reg_b_name in dep_group:
                            return True
            return False

        # Check other GPRs
        ma = re.match(r"R([0-9]+)[DWB]?", reg_a_name)
        mb = re.match(r"R([0-9]+)[DWB]?", reg_b_name)
        if ma and mb and ma.group(1) == mb.group(1):
            return True

        # No dependencies
        return False

    def is_basic_gpr(self, register):
        """Check if register is a basic general purpose register (ebi, rax, ...)"""
        if any(char.isdigit() for char in register.name) or any(
            register.name.lower().startswith(x) for x in ["mm", "xmm", "ymm", "zmm"]
        ):
            return False
        return True

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        if register is None:
            return False
        if self.is_basic_gpr(register):
            return True
        return re.match(r"R([0-9]+)[DWB]?", register.name, re.IGNORECASE)

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        if register is None or register.name is None:
            return False
        if register.name.rstrip(string.digits).lower() in [
            "mm",
            "xmm",
            "ymm",
            "zmm",
        ]:
            return True
        return False

    def get_reg_type(self, register):
        """Get register type"""
        if register is None:
            return False
        if self.is_gpr(register):
            return "gpr"
        elif self.is_vector_register(register):
            return register.name.rstrip(string.digits).lower()
        raise ValueError

    def is_flag_dependend_of(self, flag_a, flag_b):
        """Check if ``flag_a`` is dependent on ``flag_b``"""
        # we assume flags are independent of each other, e.g., CF can be read while ZF gets written
        # TODO validate this assumption
        return flag_a.name == flag_b.name

    def get_regular_source_operands(self, instruction_form):
        """Get source operand of given instruction form assuming regular src/dst behavior."""
        # if there is only one operand, assume it is a source operand
        if len(instruction_form.operands) == 1:
            return [instruction_form.operands[0]]
        # return all but last operand
        return [op for op in instruction_form.operands[0:-1]]

    def get_regular_destination_operands(self, instruction_form):
        """Get destination operand of given instruction form assuming regular src/dst behavior."""
        # if there is only one operand, assume no destination
        if len(instruction_form.operands) == 1:
            return []
        # return last operand
        return instruction_form.operands[-1:]
