#!/usr/bin/env python3
from itertools import chain

from osaca import utils
from osaca.parser.memory import MemoryOperand
from osaca.parser.operand import Operand
from osaca.parser.register import RegisterOperand
from osaca.parser.immediate import ImmediateOperand

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
        # store operand list in dict and reassign operand key/value pair
        instruction_form.semantic_operands = op_dict
        # assign LD/ST flags
        # instruction_form.flags = (
        #    instruction_form.flags if "flags" in instruction_form else []
        # )

        if self._has_load(instruction_form):
            instruction_form.flags += [INSTR_FLAGS.HAS_LD]
        if self._has_store(instruction_form):
            instruction_form.flags += [INSTR_FLAGS.HAS_ST]

    def get_reg_changes(self, instruction_form, only_postindexed=False):
        """
        Returns register changes, as dict, for insruction_form, based on operation defined in isa.

        Empty dict if no changes of registers occured. None for registers with unknown changes.
        If only_postindexed is True, only considers changes due to post_indexed memory references.
        """
        instruction_form.check_normalized()
        if instruction_form.mnemonic is None:
            return {}
        dest_reg_names = [
            (op.prefix if op.prefix is not None else "") + op.name
            for op in chain(
                instruction_form.semantic_operands["destination"],
                instruction_form.semantic_operands["src_dst"],
            )
            if isinstance(op, RegisterOperand)
        ]
        isa_data = self._isa_model.get_instruction(
            instruction_form.mnemonic, instruction_form.operands
        )

        if only_postindexed:
            for o in instruction_form.operands:
                if (
                    isinstance(o, MemoryOperand)
                    and o.base is not None
                    and isinstance(o.post_indexed, dict)
                ):
                    base_name = (o.base.prefix if o.base.prefix is not None else "") + o.base.name
                    return {
                        base_name: {
                            "name": (o.base.prefix if o.base.prefix is not None else "")
                            + o.base.name,
                            "value": o.post_indexed["value"],
                        }
                    }
            return {}

        reg_operand_names = {}  # e.g., {'rax': 'op1'}
        operand_state = {}  # e.g., {'op1': {'name': 'rax', 'value': 0}}  0 means unchanged

        for o in instruction_form.operands:
            if isinstance(o, MemoryOperand) and o.pre_indexed:
                # Assuming no isa_data.operation
                if isa_data is not None and isa_data.operation is not None:
                    raise ValueError(
                        "ISA information for pre_indexed instruction {!r} has operation set."
                        "This is currently not supprted.".format(instruction_form.line)
                    )

                base_name = (o.base.prefix if o.base.prefix is not None else "") + o.base.name
                reg_operand_names = {base_name: "op1"}
                if o.offset:
                    operand_state = {"op1": {"name": base_name, "value": o.offset.value}}
                else:
                    # no offset (e.g., with Arm9 memops) -> base is updated
                    operand_state = {"op1": None}

        if isa_data is not None and isa_data.operation is not None:
            for i, o in enumerate(instruction_form.operands):
                operand_name = "op{}".format(i + 1)

                if isinstance(o, RegisterOperand):
                    o_reg_name = (o.prefix if o.prefix is not None else "") + o.name
                    reg_operand_names[o_reg_name] = operand_name
                    operand_state[operand_name] = {"name": o_reg_name, "value": 0}
                elif isinstance(o, ImmediateOperand):
                    operand_state[operand_name] = {"value": o.value}
                elif isinstance(o, MemoryOperand):
                    # TODO lea needs some thinking about
                    pass
            exec(isa_data.operation, {}, operand_state)

        change_dict = {
            reg_name: operand_state.get(reg_operand_names.get(reg_name))
            for reg_name in dest_reg_names
        }
        return change_dict

    def _apply_found_ISA_data(self, isa_data, operands):
        """
        Create operand dictionary containing src/dst operands out of the ISA data entry and
        the oeprands of an instruction form

        If breaks_dependency_on_equal_operands is True (configuted per instruction in ISA db)
        and all operands are equal, place operand into destination only.

        :param dict isa_data: ISA DB entry
        :param list operands: operands of the instruction form
        :returns: `dict` -- operands dictionary with src/dst assignment
        """
        op_dict = {}
        op_dict["source"] = []
        op_dict["destination"] = []
        op_dict["src_dst"] = []

        # handle dependency breaking instructions
        if isa_data.breaks_dependency_on_equal_operands and operands[1:] == operands[:-1]:
            op_dict["destination"] += operands
            if isa_data.hidden_operands != []:
                op_dict["destination"] += [hop for hop in isa_data.hidden_operands]
            return op_dict

        for i, op in enumerate(isa_data.operands):
            if op.source and op.destination:
                op_dict["src_dst"].append(operands[i])
                continue
            if op.source:
                op_dict["source"].append(operands[i])
                continue
            if op.destination:
                op_dict["destination"].append(operands[i])
                continue

        # check for hidden operands like flags or registers
        if isa_data.hidden_operands != []:
            # add operand(s) to semantic_operands of instruction form
            for op in isa_data.hidden_operands:
                if isinstance(op, Operand):
                    dict_key = (
                        "src_dst"
                        if op.source and op.destination
                        else "source" if op.source else "destination"
                    )
                else:
                    dict_key = (
                        "src_dst"
                        if op["source"] and op["destination"]
                        else "source" if op["source"] else "destination"
                    )
                op_dict[dict_key].append(op)

        return op_dict

    def _has_load(self, instruction_form):
        """Check if instruction form performs a LOAD"""
        instruction_form.check_normalized()
        for operand in chain(
            instruction_form.semantic_operands["source"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(operand, MemoryOperand):
                return True
        return False

    def _has_store(self, instruction_form):
        """Check if instruction form perfroms a STORE"""
        instruction_form.check_normalized()
        for operand in chain(
            instruction_form.semantic_operands["destination"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(operand, MemoryOperand):
                return True
        return False

    def substitute_mem_address(self, operands):
        """Create memory wildcard for all memory operands"""
        return [
            self._create_reg_wildcard() if isinstance(op, MemoryOperand) else op for op in operands
        ]

    def _create_reg_wildcard(self):
        """Wildcard constructor"""
        return {"*": "*"}
