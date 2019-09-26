#!/usr/bin/env python3

import collections

from osaca.frontend import Frontend
from osaca.parser import ParserAArch64v81, ParserX86ATT
from osaca.semantics import (INSTR_FLAGS, KernelDG, MachineModel,
                             SemanticsAppender, reduce_to_section)


class KerncraftAPI(object):
    def __init__(self, arch):
        self.machine_model = MachineModel(arch=arch)
        self.semantics = SemanticsAppender(self.machine_model)
        isa = self.machine_model.get_ISA().lower()
        if isa == 'aarch64':
            self.parser = ParserAArch64v81()
        elif isa == 'x86':
            self.parser = ParserX86ATT()

    def analyze_code(self, code):
        parsed_code = self.parser.parse_file(code)
        kernel = reduce_to_section(parsed_code, self.machine_model.get_ISA())
        self.semantics.add_semantics(kernel)
        return kernel

    def create_output(self, kernel, verbose=False):
        kernel_graph = KernelDG(kernel, self.parser, self.machine_model)
        frontend = Frontend(arch=self.machine_model.get_arch())
        frontend.print_full_analysis(kernel, kernel_graph, verbose=verbose)

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
        return (self.get_lcd(kernel), self.get_cp(kernel))

    def get_cp(self, kernel):
        kernel_graph = KernelDG(kernel, self.parser, self.machine_model)
        kernel_cp = kernel_graph.get_critical_path()
        return sum([x['latency_cp'] for x in kernel_cp])

    def get_lcd(self, kernel):
        kernel_graph = KernelDG(kernel, self.parser, self.machine_model)
        lcd_dict = kernel_graph.get_loopcarried_dependencies()
        lcd = 0.0
        for dep in lcd_dict:
            lcd_tmp = sum([x['latency_lcd'] for x in lcd_dict[dep]['dependencies']])
            lcd = lcd_tmp if lcd_tmp > lcd else lcd
        return lcd
