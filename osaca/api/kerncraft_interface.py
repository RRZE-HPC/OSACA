#!/usr/bin/env python3

import collections

from osaca import Frontend
from osaca.parser import ParserAArch64v81, ParserX86ATT
from osaca.semantics import (INSTR_FLAGS, KernelDG, MachineModel, SemanticsAppender,
                             reduce_to_section)


class KerncraftAPI(object):
    def __init__(self, arch):
        self.machine_model = MachineModel(arch=arch)
        self.semantics = SemanticsAppender(self.machine_model)
        isa = self.machine_model.get_ISA()
        if isa == 'AArch64':
            self.parser = ParserAArch64v81()
        elif isa == 'x86':
            self.parser = ParserX86ATT()

    def analyze_code(self, code):
        parsed_code = self.parser.parse_file(code)
        kernel = reduce_to_section(parsed_code, self.machine_model.get_ISA())
        for i in range(len(kernel)):
            self.semantics.assign_src_dst(kernel[i])
            self.semantics.assign_tp_lt(kernel[i])
        return kernel

    def create_output(self, kernel, show_lineno=False):
        kernel_graph = KernelDG(kernel, self.parser, self.machine_model)
        frontend = Frontend(arch=self.machine_model.get_arch())
        frontend.print_throughput_analysis(kernel, show_lineno=show_lineno)
        frontend.print_latency_analysis(kernel_graph.get_critical_path())

    def get_unmatched_instruction_ratio(self, kernel):
        unmatched_counter = 0
        for instruction in kernel:
            if (
                INSTR_FLAGS.TP_UNKWN in instruction['flags']
                and INSTR_FLAGS.LT_UNKWN in instruction['flags']
            ):
                unmatched_counter += 1
        return unmatched_counter / len(kernel)

    def get_port_occupation_cycles(self, kernel):
        throughput_values = self.semantics.get_throughput_sum(kernel)
        port_names = self.machine_model['ports']
        return collections.OrderedDict(list(zip(port_names, throughput_values)))

    def get_total_throughput(self, kernel):
        return max(self.semantics.get_throughput_sum(kernel))

    def get_latency(self, kernel):
        kernel_graph = KernelDG(kernel, self.parser, self.machine_model)
        return sum([x if x['latency'] is not None else 0 for x in kernel_graph])
