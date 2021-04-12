#!/usr/bin/env python3
from itertools import chain

from osaca import utils
from osaca.parser import AttrDict, ParserAArch64, ParserX86ATT

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
    GAS_SUFFIXES = "bswlqt"

    def __init__(self, isa, path_to_yaml=None):
        self._isa = isa.lower()
        path = path_to_yaml or utils.find_datafile("isa/" + self._isa + ".yml")
        self._isa_model = MachineModel(path_to_yaml=path)
        if self._isa == "x86":
            self._parser = ParserX86ATT()
        elif self._isa == "aarch64":
            self._parser = ParserAArch64()

    def process(self, instruction_forms):
        """Process a list of instruction forms."""
        for i in instruction_forms:
            self.assign_src_dst(i)

    # get ;parser result and assign operands to
    # - source
    # - destination
    # - source/destination
    def assign_src_dst(self, instruction_form):
        """Update instruction form dictionary with source, destination and flag information."""
        # if the instruction form doesn't have operands or is None, there's nothing to do
        if instruction_form["operands"] is None or instruction_form["instruction"] is None:
            instruction_form["semantic_operands"] = AttrDict(
                {"source": [], "destination": [], "src_dst": []}
            )
            return
        # check if instruction form is in ISA yaml, otherwise apply standard operand assignment
        # (one dest, others source)
        isa_data = self._isa_model.get_instruction(
            instruction_form["instruction"], instruction_form["operands"]
        )
        if (
            isa_data is None
            and self._isa == "x86"
            and instruction_form["instruction"][-1] in self.GAS_SUFFIXES
        ):
            # Check for instruction without GAS suffix
            isa_data = self._isa_model.get_instruction(
                instruction_form["instruction"][:-1], instruction_form["operands"]
            )
        operands = instruction_form["operands"]
        op_dict = {}
        assign_default = False
        if isa_data:
            # load src/dst structure from isa_data
            op_dict = self._apply_found_ISA_data(isa_data, operands)
        else:
            # Couldn't found instruction form in ISA DB
            assign_default = True
            # check for equivalent register-operands DB entry if LD/ST
            if any(["memory" in op for op in operands]):
                operands_reg = self.substitute_mem_address(instruction_form["operands"])
                isa_data_reg = self._isa_model.get_instruction(
                    instruction_form["instruction"], operands_reg
                )
                if (
                    isa_data_reg is None
                    and self._isa == "x86"
                    and instruction_form["instruction"][-1] in self.GAS_SUFFIXES
                ):
                    # Check for instruction without GAS suffix
                    isa_data_reg = self._isa_model.get_instruction(
                        instruction_form["instruction"][:-1], operands_reg
                    )
                if isa_data_reg:
                    assign_default = False
                    op_dict = self._apply_found_ISA_data(isa_data_reg, operands)
        if assign_default:
            # no irregular operand structure, apply default
            op_dict["source"] = self._get_regular_source_operands(instruction_form)
            op_dict["destination"] = self._get_regular_destination_operands(instruction_form)
            op_dict["src_dst"] = []
        # post-process pre- and post-indexing for aarch64 memory operands
        if self._isa == "aarch64":
            for operand in [op for op in op_dict["source"] if "memory" in op]:
                post_indexed = ("post_indexed" in operand["memory"] and 
                                operand["memory"]["post_indexed"])
                pre_indexed = ("pre_indexed" in operand["memory"] and
                               operand["memory"]["pre_indexed"])
                if post_indexed or pre_indexed:
                    op_dict["src_dst"].append(
                        AttrDict.convert_dict({
                            "register": operand["memory"]["base"],
                            "pre_indexed": pre_indexed,
                            "post_indexed": post_indexed})
                    )
            for operand in [op for op in op_dict["destination"] if "memory" in op]:
                post_indexed = ("post_indexed" in operand["memory"] and 
                                operand["memory"]["post_indexed"])
                pre_indexed = ("pre_indexed" in operand["memory"] and
                               operand["memory"]["pre_indexed"])
                if post_indexed or pre_indexed:
                    op_dict["src_dst"].append(
                        AttrDict.convert_dict({
                            "register": operand["memory"]["base"],
                            "pre_indexed": pre_indexed,
                            "post_indexed": post_indexed})
                    )
        # store operand list in dict and reassign operand key/value pair
        instruction_form["semantic_operands"] = AttrDict.convert_dict(op_dict)
        # assign LD/ST flags
        instruction_form["flags"] = instruction_form["flags"] if "flags" in instruction_form else []
        if self._has_load(instruction_form):
            instruction_form["flags"] += [INSTR_FLAGS.HAS_LD]
        if self._has_store(instruction_form):
            instruction_form["flags"] += [INSTR_FLAGS.HAS_ST]

    def get_reg_changes(self, instruction_form, only_postindexed=False):
        """
        Returns register changes, as dict, for insruction_form, based on operation defined in isa.
        
        Empty dict if no changes of registers occured. None for registers with unknown changes.
        If only_postindexed is True, only considers changes due to post_indexed memory references.
        """
        if instruction_form.get('instruction') is None:
            return {}
        dest_reg_names = [op.register.get('prefix', '') + op.register.name
                          for op in chain(instruction_form.semantic_operands.destination,
                                          instruction_form.semantic_operands.src_dst)
                          if 'register' in op]
        isa_data = self._isa_model.get_instruction(
            instruction_form["instruction"], instruction_form["operands"]
        )
        if (
            isa_data is None
            and self._isa == "x86"
            and instruction_form["instruction"][-1] in self.GAS_SUFFIXES
        ):
            # Check for instruction without GAS suffix
            isa_data = self._isa_model.get_instruction(
                instruction_form["instruction"][:-1], instruction_form["operands"]
            )

        if only_postindexed:
            for o in instruction_form.operands:
                if 'post_indexed' in o.get('memory', {}):
                    base_name = o.memory.base.get('prefix', '')+o.memory.base.name
                    return {base_name: {
                        'name': o.memory.base.get('prefix', '')+o.memory.base.name,
                        'value': int(o.memory.post_indexed.value)
                    }}
            return {}

        reg_operand_names = {}  # e.g., {'rax': 'op1'}
        operand_state = {}  # e.g., {'op1': {'name': 'rax', 'value': 0}}  0 means unchanged
        
        for o in instruction_form.operands:
            if 'pre_indexed' in o.get('memory', {}):
                # Assuming no isa_data.operation
                if isa_data.get("operation", None) is not None:
                    raise ValueError(
                        "ISA information for pre-indexed instruction {!r} has operation set."
                        "This is currently not supprted.".format(instruction_form.line))
                base_name = o.memory.base.get('prefix', '')+o.memory.base.name
                reg_operand_names = {base_name: 'op1'}
                operand_state = {'op1': {
                    'name': base_name,
                    'value': int(o.memory.offset.value)
                }}

        if isa_data is not None and 'operation' in isa_data:
            for i, o in enumerate(instruction_form.operands):
                operand_name = "op{}".format(i+1)
                if "register" in o:
                    o_reg_name = o["register"].get('prefix', '')+o["register"]["name"]
                    reg_operand_names[o_reg_name] = operand_name
                    operand_state[operand_name] = {
                        'name': o_reg_name,
                        'value': 0}
                elif "immediate" in o:
                    operand_state[operand_name] = {'value': int(o["immediate"]["value"])}
                elif "memory" in o:
                    # TODO lea needs some thinking about
                    pass

            operand_changes = exec(isa_data['operation'], {}, operand_state)

        change_dict = {reg_name: operand_state.get(reg_operand_names.get(reg_name))
                       for reg_name in dest_reg_names}
        return change_dict

    def _apply_found_ISA_data(self, isa_data, operands):
        """
        Create operand dictionary containing src/dst operands out of the ISA data entry and
        the oeprands of an instruction form
        
        If breaks_pedendency_on_equal_operands is True (configuted per instruction in ISA db)
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
        if "breaks_pedendency_on_equal_operands" in isa_data and operands[1:] == operands[:-1]:
            op_dict["destination"] += operands
            if "hidden_operands" in isa_data:
                op_dict["destination"] += [
                    AttrDict.convert_dict(
                        {hop["class"]: {k: hop[k] for k in ["class", "source", "destination"]}})
                     for hop in isa_data["hidden_operands"]]
            return op_dict

        for i, op in enumerate(isa_data["operands"]):
            if op["source"] and op["destination"]:
                op_dict["src_dst"].append(operands[i])
                continue
            if op["source"]:
                op_dict["source"].append(operands[i])
                continue
            if op["destination"]:
                op_dict["destination"].append(operands[i])
                continue
        # check for hidden operands like flags or registers
        if "hidden_operands" in isa_data:
            # add operand(s) to semantic_operands of instruction form
            for op in isa_data["hidden_operands"]:
                dict_key = (
                    "src_dst"
                    if op["source"] and op["destination"]
                    else "source"
                    if op["source"]
                    else "destination"
                )
                hidden_op = {op["class"]: {}}
                key_filter = ["class", "source", "destination"]
                for key in [k for k in op.keys() if k not in key_filter]:
                    hidden_op[op["class"]][key] = op[key]
                hidden_op = AttrDict.convert_dict(hidden_op)
                op_dict[dict_key].append(hidden_op)
        return op_dict

    def _has_load(self, instruction_form):
        """Check if instruction form performs a LOAD"""
        for operand in chain(
            instruction_form["semantic_operands"]["source"],
            instruction_form["semantic_operands"]["src_dst"],
        ):
            if "memory" in operand:
                return True
        return False

    def _has_store(self, instruction_form):
        """Check if instruction form perfroms a STORE"""
        for operand in chain(
            instruction_form["semantic_operands"]["destination"],
            instruction_form["semantic_operands"]["src_dst"],
        ):
            if "memory" in operand:
                return True
        return False

    def _get_regular_source_operands(self, instruction_form):
        """Get source operand of given instruction form assuming regular src/dst behavior."""
        # if there is only one operand, assume it is a source operand
        if len(instruction_form["operands"]) == 1:
            return [instruction_form["operands"][0]]
        if self._isa == "x86":
            # return all but last operand
            return [op for op in instruction_form["operands"][0:-1]]
        elif self._isa == "aarch64":
            return [op for op in instruction_form["operands"][1:]]
        else:
            raise ValueError("Unsupported ISA {}.".format(self._isa))

    def _get_regular_destination_operands(self, instruction_form):
        """Get destination operand of given instruction form assuming regular src/dst behavior."""
        # if there is only one operand, assume no destination
        if len(instruction_form["operands"]) == 1:
            return []
        if self._isa == "x86":
            # return last operand
            return instruction_form["operands"][-1:]
        if self._isa == "aarch64":
            # return first operand
            return instruction_form["operands"][:1]
        else:
            raise ValueError("Unsupported ISA {}.".format(self._isa))

    def substitute_mem_address(self, operands):
        """Create memory wildcard for all memory operands"""
        return [self._create_reg_wildcard() if "memory" in op else op for op in operands]

    def _create_reg_wildcard(self):
        """Wildcard constructor"""
        return {"*": "*"}
