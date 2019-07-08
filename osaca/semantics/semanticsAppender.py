#!/usr/bin/env python3

import os

from osaca.parser import AttrDict
from .hw_model import MachineModel


class SemanticsAppender(object):
    def __init__(self, machine_model: MachineModel):
        self.machine_model = machine_model
        self._isa = machine_model.get_ISA()
        self._isa_model = MachineModel(path_to_yaml=self._find_file(self._isa))

    def _find_file(self, isa):
        data_dir = os.path.expanduser('~/.osaca/data/isa')
        name = os.path.join(data_dir, isa + '.yml')
        assert os.path.exists(name)
        return name

    # get parser result and assign operands to
    # - source
    # - destination
    # - source/destination
    def assign_src_dst(self, instruction_form):
        # if the instruction form doesn't have operands, there's nothing to do
        if instruction_form['operands'] is None:
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
        op_dict['operand_list'] = operands
        instruction_form['operands'] = AttrDict.convert_dict(op_dict)

    def _get_regular_source_operands(self, instruction_form):
        if self._isa == 'x86':
            return self._get_regular_source_x86ATT(instruction_form)
        if self._isa == 'AArch64':
            return self._get_regular_source_AArch64(instruction_form)

    def _get_regular_destination_operands(self, instruction_form):
        if self._isa == 'x86':
            return self._get_regular_destination_x86ATT(instruction_form)
        if self._isa == 'AArch64':
            return self._get_regular_destination_AArch64(instruction_form)

    def _get_regular_source_x86ATT(self, instruction_form):
        # return all but last operand
        sources = [
            op for op in instruction_form['operands'][0:len(instruction_form['operands']) - 1]
        ]
        return sources

    def _get_regular_source_AArch64(self, instruction_form):
        # return all but first operand
        sources = [
            op for op in instruction_form['operands'][1:len(instruction_form['operands'])]
        ]
        return sources

    def _get_regular_destination_x86ATT(self, instruction_form):
        # return last operand
        return instruction_form['operands'][-1:]

    def _get_regular_destination_AArch64(self, instruction_form):
        # return first operand
        return instruction_form['operands'][:1]
