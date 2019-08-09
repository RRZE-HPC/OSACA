#!/usr/bin/env python3

import os
import warnings
from functools import reduce

from osaca.parser import AttrDict

from .hw_model import MachineModel


class INSTR_FLAGS:
    """
    Flags used for unknown or special instructions
    """

    TP_UNKWN = 'tp_unkown'
    LT_UNKWN = 'lt_unkown'
    NOT_BOUND = 'not_bound'
    HIDDEN_LD = 'hidden_load'


class SemanticsAppender(object):
    def __init__(self, machine_model: MachineModel, path_to_yaml=None):
        self._machine_model = machine_model
        self._isa = machine_model.get_ISA()
        if path_to_yaml:
            path = path_to_yaml
        else:
            path = self._find_file(self._isa)
        self._isa_model = MachineModel(path_to_yaml=path)

    def _find_file(self, isa):
        data_dir = os.path.expanduser('~/.osaca/data/isa')
        name = os.path.join(data_dir, isa + '.yml')
        assert os.path.exists(name)
        return name

    # get parser result and assign throughput and latency value to instruction form
    # mark instruction form with semantic flags
    def assign_tp_lt(self, instruction_form):
        flags = []
        port_number = len(self._machine_model['ports'])
        instruction_data = self._machine_model.get_instruction(
            instruction_form['instruction'], instruction_form['operands']
        )
        if instruction_data:
            # instruction form in DB
            throughput = instruction_data['throughput']
            port_pressure = instruction_data['port_pressure']
            try:
                assert isinstance(port_pressure, list)
                assert len(port_pressure) == port_number
                instruction_form['port_pressure'] = port_pressure
                if sum(port_pressure) == 0 and throughput is not None:
                    # port pressure on all ports 0 --> not bound to a port
                    flags.append(INSTR_FLAGS.NOT_BOUND)
            except AssertionError:
                warnings.warn(
                    'Port pressure could not be imported correctly from database. '
                    + 'Please check entry for:\n {}'.format(instruction_form)
                )
                instruction_form['port_pressure'] = [0.0 for i in range(port_number)]
                flags.append(INSTR_FLAGS.TP_UNKWN)
            if throughput is None:
                # assume 0 cy and mark as unknown
                throughput = 0.0
                flags.append(INSTR_FLAGS.TP_UNKWN)
            latency = instruction_data['latency']
            if latency is None:
                # assume 0 cy and mark as unknown
                latency = 0.0
                flags.append(INSTR_FLAGS.LT_UNKWN)
        else:
            # instruction could not be found in DB
            # --> mark as unknown and assume 0 cy for latency/throughput
            throughput = 0.0
            latency = 0.0
            instruction_form['port_pressure'] = [0.0 for i in range(port_number)]
            flags += [INSTR_FLAGS.TP_UNKWN, INSTR_FLAGS.LT_UNKWN]
        # flatten flag list
        flags = list(set(flags))
        if 'flags' not in instruction_form:
            instruction_form['flags'] = flags
        else:
            instruction_form['flags'] += flags
        instruction_form['throughput'] = throughput
        instruction_form['latency'] = latency

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

    @staticmethod
    def get_throughput_sum(kernel):
        tp_sum = reduce(
            (lambda x, y: [sum(z) for z in zip(x, y)]),
            [instr['port_pressure'] for instr in kernel],
        )
        tp_sum = [round(x, 2) for x in tp_sum]
        return tp_sum
