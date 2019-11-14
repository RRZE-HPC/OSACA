#!/usr/bin/env python3
from itertools import chain

from osaca import utils
from osaca.parser import AttrDict, ParserAArch64v81, ParserX86ATT
from .hw_model import MachineModel


class INSTR_FLAGS:
    """
    Flags used for unknown or special instructions
    """

    LD = 'is_load_instruction'
    TP_UNKWN = 'tp_unknown'
    LT_UNKWN = 'lt_unknown'
    NOT_BOUND = 'not_bound'
    HIDDEN_LD = 'hidden_load'
    HAS_LD = 'performs_load'
    HAS_ST = 'performs_store'


class ISASemantics(object):
    def __init__(self, isa, path_to_yaml=None):
        self._isa = isa.lower()
        path = utils.find_file('isa/' + self._isa + '.yml') if not path_to_yaml else path_to_yaml
        self._isa_model = MachineModel(path_to_yaml=path)
        if self._isa == 'x86':
            self._parser = ParserX86ATT()
        elif self._isa == 'aarch64':
            self._parser = ParserAArch64v81()

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
        # if the instruction form doesn't have operands, there's nothing to do
        if instruction_form['operands'] is None:
            instruction_form['semantic_operands'] = AttrDict(
                {'source': [], 'destination': [], 'src_dst': []})
            return
        # check if instruction form is in ISA yaml, otherwise apply standard operand assignment
        # (one dest, others source)
        isa_data = self._isa_model.get_instruction(
            instruction_form['instruction'], instruction_form['operands']
        )
        operands = instruction_form['operands']
        op_dict = {}
        if isa_data is None:
            # no irregular operand structure, apply default
            op_dict['source'] = self._get_regular_source_operands(instruction_form)
            op_dict['destination'] = self._get_regular_destination_operands(instruction_form)
            op_dict['src_dst'] = []
        else:
            # load src/dst structure from isa_data
            op_dict['source'] = []
            op_dict['destination'] = []
            op_dict['src_dst'] = []
            for i, op in enumerate(isa_data['operands']):
                if op['source'] and op['destination']:
                    op_dict['src_dst'].append(operands[i])
                    continue
                if op['source']:
                    op_dict['source'].append(operands[i])
                    continue
                if op['destination']:
                    op_dict['destination'].append(operands[i])
                    continue
        # store operand list in dict and reassign operand key/value pair
        instruction_form['semantic_operands'] = AttrDict.convert_dict(op_dict)
        # assign LD/ST flags
        instruction_form['flags'] = (
            instruction_form['flags'] if 'flags' in instruction_form else []
        )
        if self._has_load(instruction_form):
            instruction_form['flags'] += [INSTR_FLAGS.HAS_LD]
        if self._has_store(instruction_form):
            instruction_form['flags'] += [INSTR_FLAGS.HAS_ST]

    def _has_load(self, instruction_form):
        for operand in chain(instruction_form['semantic_operands']['source'],
                             instruction_form['semantic_operands']['src_dst']):
            if 'memory' in operand:
                return True
        return False

    def _has_store(self, instruction_form):
        for operand in chain(instruction_form['semantic_operands']['destination'],
                             instruction_form['semantic_operands']['src_dst']):
            if 'memory' in operand:
                return True
        return False

    def _get_regular_source_operands(self, instruction_form):
        if self._isa == 'x86':
            # return all but last operand
            return [op for op in instruction_form['operands'][0:-1]]
        elif self._isa == 'aarch64':
            return [op for op in instruction_form['operands'][1:]]
        else:
            raise ValueError("Unsupported ISA {}.".format(self._isa))

    def _get_regular_destination_operands(self, instruction_form):
        if self._isa == 'x86':
            # return last operand
            return instruction_form['operands'][-1:]
        if self._isa == 'aarch64':
            # return first operand
            return instruction_form['operands'][:1]
        else:
            raise ValueError("Unsupported ISA {}.".format(self._isa))
