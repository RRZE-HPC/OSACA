#!/usr/bin/env python3

import networkx as nx


class KernelDAG(nx.DiGraph):
    def __init__(self, parsed_kernel, parser, hw_model):
        self.kernel = parsed_kernel
        self.parser = parser
        self.model = hw_model

        # self.dag = self.create_DAG()

    def check_for_loop(self, kernel):
        raise NotImplementedError

    def create_DAG(self):
        # 1. go through kernel instruction forms (as vertices)
        # 2. find edges (to dependend further instruction)
        # 3. get LT/TP value and set as edge weight
        dag = nx.DiGraph()
        for i, instruction in enumerate(self.kernel):
            throughput = self.model.get_throughput(instruction)
            latency = self.model.get_latency(instruction)
            for dep in self.find_depending(instruction, self.kernel[i + 1:]):
                dag.add_edge(
                    instruction.line_number,
                    dep.line_number,
                    latency=latency,
                    thorughput=throughput,
                )

    def find_depending(self, instruction_form, kernel):
        for dst in instruction_form.operands.destination:
            if 'register' in dst:
                # Check for read of register until overwrite
                for instr_form in kernel:
                    if self.is_read(dst.register, instr_form):
                        yield instr_form
                    elif self.is_written(dst.register, instr_form):
                        break
            elif 'memory' in dst:
                # Check if base register is altered during memory access
                if 'pre_indexed' in dst.memory or 'post_indexed' in dst.memory:
                    # Check for read of base register until overwrite
                    for instr_form in kernel:
                        if self.is_read(dst.memory.base, instr_form):
                            yield instr_form
                        elif self.is_written(dst.memory.base, instr_form):
                            break

    def is_read(self, register, instruction_form):
        is_read = False
        for src in instruction_form.operands.source:
            if 'register' in src:
                is_read = self.parser.is_reg_dependend_of(register, src.register) or is_read
            if 'memory' in src:
                if src.memory.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, src.memory.base) or is_read
                if src.memory.index is not None:
                    is_read = (
                        self.parser.is_reg_dependend_of(register, src.memory.index) or is_read
                    )
        # Check also if read in destination memory address
        for dst in instruction_form.operands.destination:
            if 'memory' in dst:
                if dst.memory.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, dst.memory.base) or is_read
                if dst.memory.index is not None:
                    is_read = (
                        self.parser.is_reg_dependend_of(register, dst.memory.index) or is_read
                    )
        return is_read

    def is_written(self, register, instruction_form):
        is_written = False
        for dst in instruction_form.operands.destination:
            if 'register' in dst:
                is_written = self.parser.is_reg_dependend_of(register, dst.register) or is_written
            if 'memory' in dst:
                if 'pre_indexed' in dst.memory or 'post_indexed' in dst.memory:
                    is_written = (
                        self.parser.is_reg_dependend_of(register, dst.memory.base) or is_written
                    )
        # Check also for possible pre- or post-indexing in memory addresses
        for src in instruction_form.operands.source:
            if 'memory' in src:
                if 'pre_indexed' in src.memory or 'post_indexed' in src.memory:
                    is_written = (
                        self.parser.is_reg_dependend_of(register, src.memory.base) or is_written
                    )
        return is_written
