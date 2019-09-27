#!/usr/bin/env python3

import os
import warnings
from functools import reduce

from osaca.parser import AttrDict, ParserAArch64v81, ParserX86ATT
from osaca.semantics import MachineModel


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


class SemanticsAppender(object):
    def __init__(self, machine_model: MachineModel, path_to_yaml=None):
        self._machine_model = machine_model
        self._isa = machine_model.get_ISA().lower()
        path = self._find_file(self._isa)
        self._isa_model = MachineModel(path_to_yaml=path)
        if self._isa == 'x86':
            self._parser = ParserX86ATT()
        elif self._isa == 'aarch64':
            self._parser = ParserAArch64v81()

    def _find_file(self, isa):
        data_dir = os.path.expanduser('~/.osaca/data/isa')
        name = os.path.join(data_dir, isa + '.yml')
        assert os.path.exists(name)
        return name

    # SUMMARY FUNCTION
    def add_semantics(self, kernel):
        for instruction_form in kernel:
            self.assign_src_dst(instruction_form)
            self.assign_tp_lt(instruction_form)
        if self._machine_model.has_hidden_loads():
            self.set_hidden_loads(kernel)

    def set_hidden_loads(self, kernel):
        loads = [instr for instr in kernel if INSTR_FLAGS.HAS_LD in instr['flags']]
        stores = [instr for instr in kernel if INSTR_FLAGS.HAS_ST in instr['flags']]
        # Filter instructions including load and store
        load_ids = [instr['line_number'] for instr in loads]
        store_ids = [instr['line_number'] for instr in stores]
        shared_ldst = list(set(load_ids).intersection(set(store_ids)))
        loads = [instr for instr in loads if instr['line_number'] not in shared_ldst]
        stores = [instr for instr in stores if instr['line_number'] not in shared_ldst]

        if len(stores) == 0 or len(loads) == 0:
            # nothing to do
            return
        if len(loads) <= len(stores):
            # Hide all loads
            for load in loads:
                load['flags'] += [INSTR_FLAGS.HIDDEN_LD]
                load['port_pressure'] = self._nullify_data_ports(load['port_pressure'])
        else:
            for store in stores:
                # Get 'closest' load instruction
                min_distance_load = min(
                    [
                        (
                            abs(load_instr['line_number'] - store['line_number']),
                            load_instr['line_number'],
                        )
                        for load_instr in loads
                        if INSTR_FLAGS.HIDDEN_LD not in load_instr['flags']
                    ]
                )
                load = [instr for instr in kernel if instr['line_number'] == min_distance_load[1]][
                    0
                ]
                # Hide load
                load['flags'] += [INSTR_FLAGS.HIDDEN_LD]
                load['port_pressure'] = self._nullify_data_ports(load['port_pressure'])

    # get parser result and assign throughput and latency value to instruction form
    # mark instruction form with semantic flags
    def assign_tp_lt(self, instruction_form):
        flags = []
        port_number = len(self._machine_model['ports'])
        if instruction_form['instruction'] is None:
            # No instruction (label, comment, ...) --> ignore
            throughput = 0.0
            latency = 0.0
            latency_wo_load = latency
            instruction_form['port_pressure'] = [0.0 for i in range(port_number)]
        else:
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
                latency_wo_load = latency
                if latency is None:
                    # assume 0 cy and mark as unknown
                    latency = 0.0
                    latency_wo_load = latency
                    flags.append(INSTR_FLAGS.LT_UNKWN)
                if INSTR_FLAGS.HAS_LD in instruction_form['flags']:
                    flags.append(INSTR_FLAGS.LD)
            else:
                # instruction could not be found in DB
                assign_unknown = True
                # check for equivalent register-operands DB entry if LD
                if INSTR_FLAGS.HAS_LD in instruction_form['flags']:
                    # --> combine LD and reg form of instruction form
                    operands = self.substitute_mem_address(instruction_form['operands'])
                    instruction_data_reg = self._machine_model.get_instruction(
                        instruction_form['instruction'], operands
                    )
                    if instruction_data_reg:
                        assign_unknown = False
                        reg_types = [
                            self._parser.get_reg_type(op['register'])
                            for op in operands['operand_list']
                            if 'register' in op
                        ]
                        load_port_pressure = self._machine_model.get_load_throughput(
                            [
                                x['memory']
                                for x in instruction_form['operands']['source']
                                if 'memory' in x
                            ][0]
                        )
                        if 'load_throughput_multiplier' in self._machine_model:
                            multiplier = self._machine_model['load_throughput_multiplier'][
                                reg_types[0]
                            ]
                            load_port_pressure = [pp * multiplier for pp in load_port_pressure]
                        throughput = max(
                            max(load_port_pressure), instruction_data_reg['throughput']
                        )
                        latency = (
                            self._machine_model.get_load_latency(reg_types[0])
                            + instruction_data_reg['latency']
                        )
                        latency_wo_load = instruction_data_reg['latency']
                        instruction_form['port_pressure'] = [
                            sum(x)
                            for x in zip(load_port_pressure, instruction_data_reg['port_pressure'])
                        ]
                if assign_unknown:
                    # --> mark as unknown and assume 0 cy for latency/throughput
                    throughput = 0.0
                    latency = 0.0
                    latency_wo_load = latency
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
        instruction_form['latency_wo_load'] = latency_wo_load
        # for later CP and loop-carried dependency analysis
        instruction_form['latency_cp'] = 0
        instruction_form['latency_lcd'] = 0

    def substitute_mem_address(self, operands):
        regs = [op for op in operands['operand_list'] if 'register' in op]
        if (
            len(regs) > 1
            and len(set([self._parser.get_reg_type(x['register']) for x in regs])) != 1
        ):
            warnings.warn('Load type could not be identified clearly.')
        reg_type = self._parser.get_reg_type(regs[0]['register'])

        source = [
            operand if 'memory' not in operand else self.convert_mem_to_reg(operand, reg_type)
            for operand in operands['source']
        ]
        destination = [
            operand if 'memory' not in operand else self.convert_mem_to_reg(operand, reg_type)
            for operand in operands['destination']
        ]
        src_dst = [
            operand if 'memory' not in operand else self.convert_mem_to_reg(operand, reg_type)
            for operand in operands['destination']
        ]
        operand_list = [
            operand if 'memory' not in operand else self.convert_mem_to_reg(operand, reg_type)
            for operand in operands['operand_list']
        ]
        return {
            'source': source,
            'destination': destination,
            'src_dst': src_dst,
            'operand_list': operand_list,
        }

    def convert_mem_to_reg(self, memory, reg_type, reg_id='0'):
        if self._isa == 'x86':
            register = {'register': {'name': reg_type + reg_id}}
        elif self._isa == 'aarch64':
            register = {'register': {'prefix': reg_type, 'name': reg_id}}
        return register

    # get ;parser result and assign operands to
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
        # assign LD/ST flags
        instruction_form['flags'] = (
            instruction_form['flags'] if 'flags' in instruction_form else []
        )
        if self._has_load(instruction_form):
            instruction_form['flags'] += [INSTR_FLAGS.HAS_LD]
        if self._has_store(instruction_form):
            instruction_form['flags'] += [INSTR_FLAGS.HAS_ST]

    def _nullify_data_ports(self, port_pressure):
        data_ports = self._machine_model.get_data_ports()
        for port in data_ports:
            index = self._machine_model.get_ports().index(port)
            port_pressure[index] = 0.0
        return port_pressure

    def _has_load(self, instruction_form):
        for operand in (
            instruction_form['operands']['source'] + instruction_form['operands']['src_dst']
        ):
            if 'memory' in operand:
                return True
        return False

    def _has_store(self, instruction_form):
        for operand in (
            instruction_form['operands']['destination'] + instruction_form['operands']['src_dst']
        ):
            if 'memory' in operand:
                return True
        return False

    def _get_regular_source_operands(self, instruction_form):
        if self._isa == 'x86':
            return self._get_regular_source_x86ATT(instruction_form)
        if self._isa == 'aarch64':
            return self._get_regular_source_AArch64(instruction_form)

    def _get_regular_destination_operands(self, instruction_form):
        if self._isa == 'x86':
            return self._get_regular_destination_x86ATT(instruction_form)
        if self._isa == 'aarch64':
            return self._get_regular_destination_AArch64(instruction_form)

    def _get_regular_source_x86ATT(self, instruction_form):
        # return all but last operand
        sources = [
            op for op in instruction_form['operands'][0: len(instruction_form['operands']) - 1]
        ]
        return sources

    def _get_regular_source_AArch64(self, instruction_form):
        # return all but first operand
        sources = [
            op for op in instruction_form['operands'][1: len(instruction_form['operands'])]
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
