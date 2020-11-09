#!/usr/bin/env python3
"""Semantics opbject responsible for architecture specific semantic operations"""

import warnings
from functools import reduce
from itertools import chain
from operator import itemgetter

from .hw_model import MachineModel
from .isa_semantics import INSTR_FLAGS, ISASemantics


class ArchSemantics(ISASemantics):
    GAS_SUFFIXES = 'bswlqt'

    def __init__(self, machine_model: MachineModel, path_to_yaml=None):
        super().__init__(machine_model.get_ISA().lower(), path_to_yaml=path_to_yaml)
        self._machine_model = machine_model
        self._isa = machine_model.get_ISA().lower()

    # SUMMARY FUNCTION
    def add_semantics(self, kernel):
        """
        Applies performance data (throughput, latency, port pressure) and source/destination
        distribution to each instruction of a given kernel.

        :param list kernel: kernel to apply semantics
        """
        for instruction_form in kernel:
            self.assign_src_dst(instruction_form)
            self.assign_tp_lt(instruction_form)
        if self._machine_model.has_hidden_loads():
            self.set_hidden_loads(kernel)

    def assign_optimal_throughput(self, kernel):
        """
        Assign optimal throughput port pressure to a kernel. This is done in steps of ``0.01cy``.

        :param list kernel: kernel to apply optimal port utilization
        """
        INC = 0.01
        kernel.reverse()
        port_list = self._machine_model.get_ports()
        for instruction_form in kernel:
            for uop in instruction_form['port_uops']:
                cycles = uop[0]
                ports = list(uop[1])
                indices = [port_list.index(p) for p in ports]
                # check if port sum of used ports for uop are unbalanced
                port_sums = self._to_list(itemgetter(*indices)(self.get_throughput_sum(kernel)))
                instr_ports = self._to_list(
                    itemgetter(*indices)(instruction_form['port_pressure'])
                )
                if len(set(port_sums)) > 1:
                    # balance ports
                    # init list for keeping track of the current change
                    differences = [cycles / len(ports)  for p in ports]
                    for _ in range(int(cycles * (1 / INC))):
                        if len(instr_ports) == 1:
                            # no balancing possible anymore
                            break
                        max_port_idx = port_sums.index(max(port_sums))
                        min_port_idx = port_sums.index(min(port_sums))
                        instr_ports[max_port_idx] -= INC
                        instr_ports[min_port_idx] += INC
                        differences[max_port_idx] -= INC
                        differences[min_port_idx] += INC
                        # instr_ports = [round(p, 2) for p in instr_ports]
                        self._itemsetter(*indices)(instruction_form['port_pressure'], *instr_ports)
                        # check if min port is zero
                        if round(min(instr_ports), 2) <= 0:
                            # if port_pressure is not exactly 0.00, add the residual to
                            # the former port
                            if min(instr_ports) != 0.0:
                                min_port_idx = port_sums.index(min(port_sums))
                                instr_ports[min_port_idx] += min(instr_ports)
                                differences[min_port_idx] += min(instr_ports)
                                # we don't need to decrease difference for other port, just
                                # delete it
                                del differences[instr_ports.index(min(instr_ports))]
                                self._itemsetter(*indices)(
                                    instruction_form['port_pressure'], *instr_ports
                                )
                                zero_index = [
                                    p
                                    for p in indices
                                    if round(instruction_form['port_pressure'][p], 2) == 0
                                ][0]
                                instruction_form['port_pressure'][zero_index] = 0.0
                            # Remove from further balancing
                            indices = [
                                p for p in indices if instruction_form['port_pressure'][p] > 0
                            ]
                            instr_ports = self._to_list(
                                itemgetter(*indices)(instruction_form['port_pressure'])
                            )
                        # never remove more than the fixed utilization per uop and port, i.e., 
                        # cycles/len(ports)
                        if round(min(differences), 2) <= 0:
                            # don't worry if port_pressure isn't exactly 0 and just
                            # remove from further balancing by deleting index since
                            # pressure is not 0
                            del indices[differences.index(min(differences))]
                            instr_ports = self._to_list(
                                 itemgetter(*indices)(instruction_form['port_pressure'])
                            )
                            del differences[differences.index(min(differences))]
                        port_sums = self._to_list(
                            itemgetter(*indices)(self.get_throughput_sum(kernel))
                        )
        kernel.reverse()

    def set_hidden_loads(self, kernel):
        """Hide loads behind stores if architecture supports hidden loads (depricated)"""
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
        """Assign throughput and latency to an instruction form."""
        flags = []
        port_number = len(self._machine_model['ports'])
        if instruction_form['instruction'] is None:
            # No instruction (label, comment, ...) --> ignore
            throughput = 0.0
            latency = 0.0
            latency_wo_load = latency
            instruction_form['port_pressure'] = [0.0 for i in range(port_number)]
            instruction_form['port_uops'] = []
        else:
            instruction_data = self._machine_model.get_instruction(
                instruction_form['instruction'], instruction_form['operands']
            )
            if (
                not instruction_data
                and self._isa == 'x86'
                and instruction_form['instruction'][-1] in self.GAS_SUFFIXES
            ):
                # check for instruction without GAS suffix
                instruction_data = self._machine_model.get_instruction(
                    instruction_form['instruction'][:-1], instruction_form['operands']
                )
            if instruction_data:
                # instruction form in DB
                (
                    throughput,
                    port_pressure,
                    latency,
                    latency_wo_load,
                ) = self._handle_instruction_found(
                    instruction_data, port_number, instruction_form, flags
                )
            else:
                # instruction could not be found in DB
                assign_unknown = True
                # check for equivalent register-operands DB entry if LD
                if (
                    INSTR_FLAGS.HAS_LD in instruction_form['flags']
                    or INSTR_FLAGS.HAS_ST in instruction_form['flags']
                ):
                    # dynamically combine LD/ST and reg form of instruction form
                    # substitute mem and look for reg-only variant
                    operands = self.substitute_mem_address(instruction_form['operands'])
                    instruction_data_reg = self._machine_model.get_instruction(
                        instruction_form['instruction'], operands
                    )
                    if (
                        not instruction_data_reg
                        and self._isa == 'x86'
                        and instruction_form['instruction'][-1] in self.GAS_SUFFIXES
                    ):
                        # check for instruction without GAS suffix
                        instruction_data_reg = self._machine_model.get_instruction(
                            instruction_form['instruction'][:-1], operands
                        )
                    if instruction_data_reg:
                        assign_unknown = False
                        reg_type = self._parser.get_reg_type(
                            instruction_data_reg['operands'][
                                operands.index(self._create_reg_wildcard())
                            ]
                        )
                        data_port_pressure = [0.0 for _ in range(port_number)]
                        data_port_uops = []
                        if INSTR_FLAGS.HAS_LD in instruction_form['flags']:
                            # LOAD performance data
                            data_port_uops = self._machine_model.get_load_throughput(
                                [
                                    x['memory']
                                    for x in instruction_form['semantic_operands']['source']
                                    + instruction_form['semantic_operands']['src_dst']
                                    if 'memory' in x
                                ][0]
                            )
                            data_port_pressure = self._machine_model.average_port_pressure(
                                data_port_uops
                            )
                            if 'load_throughput_multiplier' in self._machine_model:
                                multiplier = self._machine_model['load_throughput_multiplier'][
                                    reg_type
                                ]
                                data_port_pressure = [pp * multiplier for pp in data_port_pressure]
                        if INSTR_FLAGS.HAS_ST in instruction_form['flags']:
                            # STORE performance data
                            destinations = (
                                instruction_form['semantic_operands']['destination']
                                + instruction_form['semantic_operands']['src_dst']
                            )
                            st_data_port_uops = self._machine_model.get_store_throughput(
                                [x['memory'] for x in destinations if 'memory' in x][0]
                            )
                            # zero data port pressure and remove HAS_ST flag if
                            #   - no mem operand in dst &&
                            #   - all mem operands in src_dst are pre-/post-indexed
                            # since it is no mem store
                            if (
                                self._isa == 'aarch64'
                                and 'memory'
                                not in instruction_form['semantic_operands']['destination']
                                and all(
                                    [
                                        'post_indexed' in op['memory']
                                        or 'pre_indexed' in op['memory']
                                        for op in instruction_form['semantic_operands']['src_dst']
                                        if 'memory' in op
                                    ]
                                )
                            ):
                                st_data_port_uops = []
                                instruction_form['flags'].remove(INSTR_FLAGS.HAS_ST)

                            # sum up all data ports in case for LOAD and STORE
                            st_data_port_pressure = self._machine_model.average_port_pressure(
                                st_data_port_uops
                            )
                            data_port_pressure = [
                                sum(x) for x in zip(data_port_pressure, st_data_port_pressure)
                            ]
                            data_port_uops += st_data_port_uops
                        throughput = max(
                            max(data_port_pressure), instruction_data_reg['throughput']
                        )
                        latency = instruction_data_reg['latency']
                        # Add LD and ST latency
                        latency += (
                            self._machine_model.get_load_latency(reg_type)
                            if INSTR_FLAGS.HAS_LD in instruction_form['flags']
                            else 0
                        )
                        latency += (
                            self._machine_model.get_store_latency(reg_type)
                            if INSTR_FLAGS.HAS_ST in instruction_form['flags']
                            else 0
                        )
                        latency_wo_load = instruction_data_reg['latency']
                        # add latency of ADD if post- or pre-indexed load
                        # TODO more investigation: check dot-graph, wrong latency distribution!
                        # if (
                        #     latency_wo_load == 0
                        #     and self._isa == 'aarch64'
                        #     and any(
                        #         [
                        #             'post_indexed' in op['memory'] or 'pre_indexed' in op['memory']
                        #             for op in instruction_form['operands']
                        #             if 'memory' in op
                        #         ]
                        #     )
                        # ):
                        #     latency_wo_load = 1.0
                        instruction_form['port_pressure'] = [
                            sum(x)
                            for x in zip(
                                data_port_pressure,
                                self._machine_model.average_port_pressure(
                                    instruction_data_reg['port_pressure']
                                ),
                            )
                        ]
                        instruction_form['port_uops'] = list(
                            chain(instruction_data_reg['port_pressure'], data_port_uops)
                        )

                if assign_unknown:
                    # --> mark as unknown and assume 0 cy for latency/throughput
                    throughput = 0.0
                    latency = 0.0
                    latency_wo_load = latency
                    instruction_form['port_pressure'] = [0.0 for i in range(port_number)]
                    instruction_form['port_uops'] = []
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

    def _handle_instruction_found(self, instruction_data, port_number, instruction_form, flags):
        """Apply performance data to instruction if it was found in the archDB"""
        throughput = instruction_data['throughput']
        port_pressure = self._machine_model.average_port_pressure(
            instruction_data['port_pressure']
        )
        instruction_form['port_uops'] = instruction_data['port_pressure']
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
            instruction_form['port_uops'] = []
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
        return throughput, port_pressure, latency, latency_wo_load

    def convert_op_to_reg(self, reg_type, reg_id='0'):
        """Create register operand for a memory addressing operand"""
        if self._isa == 'x86':
            if reg_type == 'gpr':
                register = {'register': {'name': 'r' + str(int(reg_id) + 9)}}
            else:
                register = {'register': {'name': reg_type + reg_id}}
        elif self._isa == 'aarch64':
            register = {'register': {'prefix': reg_type, 'name': reg_id}}
        return register

    def _nullify_data_ports(self, port_pressure):
        """Set all ports to 0.0 for the ports of a machine model"""
        data_ports = self._machine_model.get_data_ports()
        for port in data_ports:
            index = self._machine_model.get_ports().index(port)
            port_pressure[index] = 0.0
        return port_pressure

    def _itemsetter(self, *items):
        if len(items) == 1:
            item = items[0]

            def g(obj, value):
                obj[item] = value
        else:
            def g(obj, *values):
                for item, value in zip(items, values):
                    obj[item] = value

        return g

    def _to_list(self, obj):
        if isinstance(obj, tuple):
            return list(obj)
        else:
            return [obj]

    @staticmethod
    def get_throughput_sum(kernel):
        """Get the overall throughput sum separated by port of all instructions of a kernel."""
        # ignoring all lines with throughput == 0.0, because there won't be anything to sum up
        # typically comment, label and non-instruction lines
        port_pressures = [instr['port_pressure'] for instr in kernel if instr['throughput'] != 0.0]
        # Essentially summing up each columns of port_pressures, where each column is one port
        # and each row is one line of the kernel
        # round is necessary to ensure termination of ArchsSemantics.assign_optimal_throughput
        tp_sum = [round(sum(col), 2) for col in zip(*port_pressures)]
        return tp_sum
