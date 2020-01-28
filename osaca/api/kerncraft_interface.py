#!/usr/bin/env python3

import collections
import sys
from io import StringIO

from osaca.frontend import Frontend
from osaca.parser import ParserAArch64v81, ParserX86ATT
from osaca.semantics import (INSTR_FLAGS, KernelDG, MachineModel,
                             ArchSemantics, reduce_to_section)


# Stolen from https://stackoverflow.com/a/16571630
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class KerncraftAPI(object):
    def __init__(self, arch, code):
        self.machine_model = MachineModel(arch=arch)
        self.semantics = ArchSemantics(self.machine_model)
        isa = self.machine_model.get_ISA().lower()
        if isa == 'aarch64':
            self.parser = ParserAArch64v81()
        elif isa == 'x86':
            self.parser = ParserX86ATT()

        parsed_code = self.parser.parse_file(code)
        self.kernel = reduce_to_section(parsed_code, self.machine_model.get_ISA())
        self.semantics.add_semantics(self.kernel)

    def create_output(self, verbose=False):
        kernel_graph = KernelDG(self.kernel, self.parser, self.machine_model)
        frontend = Frontend(arch=self.machine_model.get_arch())
        return frontend.full_analysis(self.kernel, kernel_graph, verbose=verbose)

    def get_unmatched_instruction_ratio(self):
        unmatched_counter = 0
        for instruction in self.kernel:
            if (
                INSTR_FLAGS.TP_UNKWN in instruction['flags']
                and INSTR_FLAGS.LT_UNKWN in instruction['flags']
            ):
                unmatched_counter += 1
        return unmatched_counter / len(self.kernel)

    def get_port_occupation_cycles(self):
        throughput_values = self.semantics.get_throughput_sum(self.kernel)
        port_names = self.machine_model['ports']
        return collections.OrderedDict(list(zip(port_names, throughput_values)))

    def get_total_throughput(self):
        return max(self.semantics.get_throughput_sum(self.kernel))

    def get_latency(self):
        return (self.get_lcd(), self.get_cp())

    def get_cp(self):
        kernel_graph = KernelDG(self.kernel, self.parser, self.machine_model)
        kernel_cp = kernel_graph.get_critical_path()
        return sum([x['latency_cp'] for x in kernel_cp])

    def get_lcd(self):
        kernel_graph = KernelDG(self.kernel, self.parser, self.machine_model)
        lcd_dict = kernel_graph.get_loopcarried_dependencies()
        lcd = 0.0
        for dep in lcd_dict:
            lcd_tmp = sum([x['latency_lcd'] for x in lcd_dict[dep]['dependencies']])
            lcd = lcd_tmp if lcd_tmp > lcd else lcd
        return lcd
