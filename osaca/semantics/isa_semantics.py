#!/usr/bin/env python3
from itertools import chain

from osaca import utils
from osaca.parser import ParserAArch64, ParserX86ATT, ParserRISCV
from osaca.parser.memory import MemoryOperand
from osaca.parser.operand import Operand
from osaca.parser.register import RegisterOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.instruction_form import InstructionForm

from .hw_model import MachineModel


class INSTR_FLAGS:
    """
    Flags used for unknown or special instructions
    """

    LD = "is_load_instruction"
    TP_UNKWN = "tp_unknown"
    LT_UNKWN = "lt_unknown"
    NOT_BOUND = "not_bound"
    HIDDEN_LD = "hidden_load"
    HAS_LD = "performs_load"
    HAS_ST = "performs_store"


class ISASemantics(object):
    def __init__(self, parser, path_to_yaml=None):
        path = path_to_yaml or utils.find_datafile("isa/" + parser.isa() + ".yml")
        self._isa_model = MachineModel(path_to_yaml=path)
        self._parser = parser

    @property
    def parser(self):
        return self._parser

    @property
    def isa_model(self):
        return self._isa_model

    def process(self, instruction_forms):
        """Process a list of instruction forms."""
        for i in instruction_forms:
            i.check_normalized()
            self.assign_src_dst(i)

    # get ;parser result and assign operands to
    # - source
    # - destination
    # - source/destination
    def assign_src_dst(self, instruction_form):
        """Update instruction form dictionary with source, destination and flag information."""
        instruction_form.check_normalized()
        # if the instruction form doesn't have operands or is None, there's nothing to do
        if instruction_form.operands is None or instruction_form.mnemonic is None:
            instruction_form.semantic_operands = {"source": [], "destination": [], "src_dst": []}
            return
        # check if instruction form is in ISA yaml, otherwise apply standard operand assignment
        # (one dest, others source)
        isa_data = self._isa_model.get_instruction(
            instruction_form.mnemonic, instruction_form.operands
        )
        if (
            isa_data is None
            and self._parser.isa() == "x86"
            and instruction_form.mnemonic[-1] in self._parser.GAS_SUFFIXES
        ):
            # Check for instruction without GAS suffix
            isa_data = self._isa_model.get_instruction(
                instruction_form.mnemonic[:-1], instruction_form.operands
            )
        if isa_data is None and self._parser.isa() == "aarch64" and "." in instruction_form.mnemonic:
            # Check for instruction without shape/cc suffix
            suffix_start = instruction_form.mnemonic.index(".")
            isa_data = self._isa_model.get_instruction(
                instruction_form.mnemonic[:suffix_start], instruction_form.operands
            )
        if isa_data is None and self._parser.isa() == "riscv" and "." in instruction_form.mnemonic:
            # Check for instruction without vector/FP suffix (.v, .vv, .vf, .s, .d etc.)
            suffix_start = instruction_form.mnemonic.index(".")
            isa_data = self._isa_model.get_instruction(
                instruction_form.mnemonic[:suffix_start], instruction_form.operands
            )
        operands = instruction_form.operands
        op_dict = {}

        assign_default = False
        if isa_data:
            # load src/dst structure from isa_data
            op_dict = self._apply_found_ISA_data(isa_data, operands)
        else:
            # Couldn't found instruction form in ISA DB
            assign_default = True
            # check for equivalent register-operands DB entry if LD/ST
            if any([isinstance(op, MemoryOperand) for op in operands]):
                operands_reg = self.substitute_mem_address(instruction_form.operands)
                isa_data_reg = self._isa_model.get_instruction(
                    instruction_form.mnemonic, operands_reg
                )
                if isa_data_reg:
                    assign_default = False
                    op_dict = self._apply_found_ISA_data(isa_data_reg, operands)

        if assign_default:
            # no irregular operand structure, apply default
            op_dict["source"] = self._parser.get_regular_source_operands(instruction_form)
            op_dict["destination"] = self._parser.get_regular_destination_operands(
                instruction_form
            )
            op_dict["src_dst"] = []
            # handle Xd! registers in aarch64
            if any(
                [
                    isinstance(op, RegisterOperand) and op.pre_indexed
                    for op in instruction_form.operands
                ]
            ):
                src_dst_regs = [
                    op
                    for op in instruction_form.operands
                    if (isinstance(op, RegisterOperand) and op.pre_indexed)
                ]
                for reg in src_dst_regs:
                    if reg in op_dict["source"]:
                        op_dict["source"].remove(reg)
                        op_dict["src_dst"].append(reg)
        # post-process pre- and post-indexing for aarch64 memory operands
        if self._parser.isa() == "aarch64":
            for operand in [op for op in op_dict["source"] if isinstance(op, MemoryOperand)]:
                post_indexed = operand.post_indexed
                pre_indexed = operand.pre_indexed
                if (
                    post_indexed
                    or pre_indexed
                    or (isinstance(post_indexed, dict) and "value" in post_indexed)
                ):
                    new_op = operand.base
                    new_op.pre_indexed = pre_indexed
                    new_op.post_indexed = post_indexed
                    op_dict["src_dst"].append(new_op)
            for operand in [op for op in op_dict["destination"] if isinstance(op, MemoryOperand)]:
                post_indexed = operand.post_indexed
                pre_indexed = operand.pre_indexed
                if (
                    post_indexed
                    or pre_indexed
                    or (isinstance(post_indexed, dict) and "value" in post_indexed)
                ):
                    new_op = operand.base
                    new_op.pre_indexed = pre_indexed
                    new_op.post_indexed = post_indexed
                    op_dict["src_dst"].append(new_op)
        # check if special mem instruction needs flags
        has_load = False
        has_store = False
        for i in op_dict["source"]:
            if isinstance(i, MemoryOperand):
                has_load = True
        for i in op_dict["destination"]:
            if isinstance(i, MemoryOperand):
                has_store = True
        if has_load:
            instruction_form.flags += [INSTR_FLAGS.HAS_LD]
        if has_store:
            instruction_form.flags += [INSTR_FLAGS.HAS_ST]
        # write operand dict to instruction_form
        instruction_form.semantic_operands = op_dict
        # get additional reg changes
        if self._parser.isa() == "aarch64":
            instruction_form.semantic_operands.update(
                {"post_increment": self.get_reg_changes(instruction_form)}
            )

    def get_reg_changes(self, instruction_form, only_postindexed=False):
        """
        Returns dictionary of registers (key) and their address change (value) due to postindexing in aarch64 at runtime.

        :param list instruction_form: instruction form to extract register change info
        :param bool only_postindexed: if true, only post-indexed changes are evaluated, defaults to False.
        :returns `dict of register names to address change` -- dict mapping from register name to address change expression.
        """
        instr_reg_changes = {}
        # only needed for aarch64
        if self._parser.isa() != "aarch64":
            return instr_reg_changes
        # find all post- and pre-indexed memory operands
        for source in instruction_form.semantic_operands["source"]:
            if isinstance(source, MemoryOperand):
                post_indexed = source.post_indexed
                pre_indexed = source.pre_indexed
                if only_postindexed and not post_indexed:
                    continue
                if isinstance(post_indexed, dict):
                    if "value" in post_indexed:
                        if isinstance(post_indexed["value"], int):
                            if (
                                source.base.name
                                not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                            ):
                                instr_reg_changes[source.base.name] = post_indexed["value"]
                                source.base.post_indexed = post_indexed["value"]
                        elif isinstance(post_indexed["value"], RegisterOperand):
                            reg_name = post_indexed["value"].name
                            if (
                                source.base.name
                                not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                            ):
                                instr_reg_changes[source.base.name] = (
                                    1
                                    if "subtract" not in post_indexed or not post_indexed["subtract"]
                                    else -1
                                ) * post_indexed["value"]
                                source.base.post_indexed = (
                                    1
                                    if "subtract" not in post_indexed or not post_indexed["subtract"]
                                    else -1
                                ) * post_indexed["value"]
                        elif isinstance(post_indexed["value"], ImmediateOperand):
                            if (
                                source.base.name
                                not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                            ):
                                instr_reg_changes[source.base.name] = post_indexed["value"].value
                                source.base.post_indexed = post_indexed["value"].value
                elif post_indexed:
                    if (
                        source.base.name
                        not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                    ):
                        instr_reg_changes[source.base.name] = source.offset
                        source.base.post_indexed = source.offset
                elif pre_indexed:
                    # for writes, the pre-indexed register is also on the destination side
                    # so the instruction form should list it only once as a src_dst register
                    # that only needs to be done the first time
                    if (
                        source.base.name
                        not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                        and source.base.name
                        not in instruction_form.semantic_operands.get("pre_indexed", [])
                    ):
                        instruction_form.semantic_operands.setdefault("pre_indexed", []).append(
                            source.base.name
                        )
        for dest in instruction_form.semantic_operands["destination"]:
            if isinstance(dest, MemoryOperand):
                post_indexed = dest.post_indexed
                pre_indexed = dest.pre_indexed
                if only_postindexed and not post_indexed:
                    continue
                if isinstance(post_indexed, dict):
                    if "value" in post_indexed:
                        if isinstance(post_indexed["value"], int):
                            if (
                                dest.base.name
                                not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                            ):
                                instr_reg_changes[dest.base.name] = post_indexed["value"]
                                dest.base.post_indexed = post_indexed["value"]
                        elif isinstance(post_indexed["value"], RegisterOperand):
                            if (
                                dest.base.name
                                not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                            ):
                                instr_reg_changes[dest.base.name] = (
                                    1
                                    if "subtract" not in post_indexed or not post_indexed["subtract"]
                                    else -1
                                ) * post_indexed["value"]
                                dest.base.post_indexed = (
                                    1
                                    if "subtract" not in post_indexed or not post_indexed["subtract"]
                                    else -1
                                ) * post_indexed["value"]
                        elif isinstance(post_indexed["value"], ImmediateOperand):
                            if (
                                dest.base.name
                                not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                            ):
                                instr_reg_changes[dest.base.name] = post_indexed["value"].value
                                dest.base.post_indexed = post_indexed["value"].value
                elif post_indexed:
                    if (
                        dest.base.name
                        not in [r.name for r in instruction_form.semantic_operands["src_dst"]]
                    ):
                        instr_reg_changes[dest.base.name] = dest.offset
                        dest.base.post_indexed = dest.offset
                elif pre_indexed:
                    # Handled by source part iff same register is used in pre-indexed base
                    pass
        return instr_reg_changes

    def _apply_found_ISA_data(self, isa_data, operands):
        """Applies instruction configuration to operand dict"""
        op_dict = {
            "source": [],
            "destination": [],
            "src_dst": [],
        }
        instruction_form = None
        
        # Create a temporary instruction form if we need to use get_regular_*_operands
        if len(operands) > 0:
            instruction_form = InstructionForm(
                mnemonic="temp",
                operands=operands
            )
            
        try:
            # Special handling for RISC-V InstructionForm objects
            if isinstance(isa_data, InstructionForm):
                # For RISC-V, first operand is destination, rest are sources
                if len(operands) > 0:
                    op_dict["destination"] = [operands[0]]
                if len(operands) > 1:
                    op_dict["source"] = operands[1:]
                return op_dict
                
            # Get operands distribution
            for idx, op_flag in enumerate(isa_data["operands"]):
                op = operands[idx]
                if op_flag == "src":
                    op_dict["source"].append(op)
                elif op_flag == "dst":
                    op_dict["destination"].append(op)
                elif op_flag == "src_dst":
                    op_dict["src_dst"].append(op)
                else:
                    raise ValueError(
                        "Unknown operand flag: {} at index {} in {}".format(
                            op_flag, idx, str(isa_data)
                        )
                    )
        except (ValueError, KeyError, IndexError, TypeError) as e:
            # TODO: add logger with debugging message
            # print(str(e), operands)
            # if instruction has no operands in ISA model yaml, assign regular semantic
            # i.e., first operand is destination, others are sources
            if instruction_form:
                op_dict["source"] = self._parser.get_regular_source_operands(instruction_form)
                op_dict["destination"] = self._parser.get_regular_destination_operands(instruction_form)
                op_dict["src_dst"] = []
        return op_dict

    def _has_load(self, instruction_form):
        """Check if the instruction has loads from memory"""
        try:
            memops = [
                op
                for op in instruction_form.semantic_operands["source"]
                if isinstance(op, MemoryOperand)
            ]
            return len(memops) > 0
        except (AttributeError, KeyError, TypeError):
            return False

    def _has_store(self, instruction_form):
        """Check if the instruction has stores to memory"""
        try:
            memops = [
                op
                for op in instruction_form.semantic_operands["destination"]
                if isinstance(op, MemoryOperand)
            ]
            return len(memops) > 0
        except (AttributeError, KeyError, TypeError):
            return False

    def _get_regular_source_operands(self, instruction_form):
        """Get source operand of given instruction form assuming regular src/dst behavior."""
        # if there is only one operand, assume it is a source operand
        if len(instruction_form.operands) == 1:
            return [instruction_form.operands[0]]
        if self._parser.isa() == "x86":
            # return all but last operand
            return [op for op in instruction_form.operands[0:-1]]
        elif self._parser.isa() == "aarch64":
            return [op for op in instruction_form.operands[1:]]
        elif self._parser.isa() == "riscv":
            # For RISC-V, the first operand is typically the destination,
            # and the rest are sources
            return [op for op in instruction_form.operands[1:]]
        else:
            raise ValueError("Unsupported ISA {}.".format(self._parser.isa()))

    def _get_regular_destination_operands(self, instruction_form):
        """Get destination operand of given instruction form assuming regular src/dst behavior."""
        # if there is only one operand, assume it is a source operand
        if len(instruction_form.operands) == 1:
            return []
        if self._parser.isa() == "x86":
            # return last operand
            return instruction_form.operands[-1:]
        if self._parser.isa() == "aarch64":
            # return first operand
            return instruction_form.operands[:1]
        elif self._parser.isa() == "riscv":
            # For RISC-V, the first operand is typically the destination
            return instruction_form.operands[:1]
        else:
            raise ValueError("Unsupported ISA {}.".format(self._parser.isa()))

    def substitute_mem_address(self, operands):
        """Create memory wildcard for all memory operands"""
        operands_reg = []
        for operand in operands:
            if isinstance(operand, MemoryOperand):
                operands_reg.append(self._create_reg_wildcard())
            else:
                operands_reg.append(operand)
        return operands_reg

    def _create_reg_wildcard(self):
        """Create register wildcard operand"""
        return RegisterOperand("reg")
