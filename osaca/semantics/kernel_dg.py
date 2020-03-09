#!/usr/bin/env python3

import copy
from itertools import chain, product

import networkx as nx

from osaca.parser import AttrDict
from osaca.semantics import INSTR_FLAGS, MachineModel


class KernelDG(nx.DiGraph):
    def __init__(self, parsed_kernel, parser, hw_model: MachineModel):
        self.kernel = parsed_kernel
        self.parser = parser
        self.model = hw_model
        self.dg = self.create_DG(self.kernel)
        self.loopcarried_deps = self.check_for_loopcarried_dep(self.kernel)

    def create_DG(self, kernel):
        """
        Create directed graph from given kernel

        :param kernel: Parsed asm kernel with assigned semantic information
        :type kerne: list
        :returns: :class:`~nx.DiGraph` -- directed graph object
        """
        # 1. go through kernel instruction forms and add them as node attribute
        # 2. find edges (to dependend further instruction)
        # 3. get LT value and set as edge weight
        dg = nx.DiGraph()
        for i, instruction_form in enumerate(kernel):
            dg.add_node(instruction_form['line_number'])
            dg.nodes[instruction_form['line_number']]['instruction_form'] = instruction_form
            # add load as separate node if existent
            if (
                INSTR_FLAGS.HAS_LD in instruction_form['flags']
                and INSTR_FLAGS.LD not in instruction_form['flags']
            ):
                # add new node
                dg.add_node(instruction_form['line_number'] + 0.1)
                dg.nodes[instruction_form['line_number'] + 0.1][
                    'instruction_form'
                ] = instruction_form
                # and set LD latency as edge weight
                dg.add_edge(
                    instruction_form['line_number'] + 0.1,
                    instruction_form['line_number'],
                    latency=instruction_form['latency'] - instruction_form['latency_wo_load'],
                )
            for dep in self.find_depending(instruction_form, kernel[i + 1 :]):
                edge_weight = (
                    instruction_form['latency']
                    if 'latency_wo_load' not in instruction_form
                    else instruction_form['latency_wo_load']
                )
                dg.add_edge(
                    instruction_form['line_number'], dep['line_number'], latency=edge_weight
                )
                dg.nodes[dep['line_number']]['instruction_form'] = dep
        return dg

    def check_for_loopcarried_dep(self, kernel):
        """
        Try to find loop-carried dependencies in given kernel.

        :param kernel: Parsed asm kernel with assigned semantic information
        :type kernel: list
        :returns: `dict` -- dependency dictionary with all cyclic LCDs
        """
        multiplier = len(kernel) + 1
        # increase line number for second kernel loop
        kernel_length = len(kernel)
        first_line_no = kernel[0].line_number
        kernel_copy = [AttrDict.convert_dict(d) for d in copy.deepcopy(kernel)]
        tmp_kernel = kernel + kernel_copy
        for i, instruction_form in enumerate(tmp_kernel[kernel_length:]):
            tmp_kernel[i + kernel_length].line_number = instruction_form.line_number * multiplier
        # get dependency graph
        dg = self.create_DG(tmp_kernel)

        # build cyclic loop-carried dependencies
        loopcarried_deps = [
            (node, list(nx.algorithms.simple_paths.all_simple_paths(dg, node, node * multiplier)))
            for node in dg.nodes
            if node < first_line_no * multiplier and node == int(node)
        ]
        # filter others and create graph
        loopcarried_deps = list(
            chain.from_iterable(
                [list(product([dep_chain[0]], dep_chain[1])) for dep_chain in loopcarried_deps]
            )
        )
        # adjust line numbers, filter duplicates
        # and add reference to kernel again
        loopcarried_deps_dict = {}
        tmp_list = []
        for i, dep in enumerate(loopcarried_deps):
            nodes = [int(n / multiplier) for n in dep[1] if n >= first_line_no * multiplier]
            loopcarried_deps[i] = (dep[0], nodes)
        for dep in loopcarried_deps:
            is_subset = False
            for other_dep in [x for x in loopcarried_deps if x[0] != dep[0]]:
                if set(dep[1]).issubset(set(other_dep[1])) and dep[0] in other_dep[1]:
                    is_subset = True
            if not is_subset:
                tmp_list.append(dep)
        loopcarried_deps = tmp_list
        for dep in loopcarried_deps:
            nodes = []
            for n in dep[1]:
                self._get_node_by_lineno(int(n))['latency_lcd'] = 0
            for n in dep[1]:
                node = self._get_node_by_lineno(int(n))
                if int(n) != n and int(n) in dep[1]:
                    node['latency_lcd'] += node['latency'] - node['latency_wo_load']
                else:
                    node['latency_lcd'] += node['latency_wo_load']
                nodes.append(node)
            loopcarried_deps_dict[dep[0]] = {
                'root': self._get_node_by_lineno(dep[0]),
                'dependencies': nodes,
            }

        return loopcarried_deps_dict

    def _get_node_by_lineno(self, lineno):
        """Return instruction form with line number ``lineno`` from  kernel"""
        return [instr for instr in self.kernel if instr.line_number == lineno][0]

    def get_critical_path(self):
        """Find and return critical path after the creation of a directed graph."""
        if nx.algorithms.dag.is_directed_acyclic_graph(self.dg):
            longest_path = nx.algorithms.dag.dag_longest_path(self.dg, weight='latency')
            for line_number in longest_path:
                self._get_node_by_lineno(int(line_number))['latency_cp'] = 0
            # add LD latency to instruction
            for line_number in longest_path:
                node = self._get_node_by_lineno(int(line_number))
                if line_number != int(line_number) and int(line_number) in longest_path:
                    node['latency_cp'] += self.dg.edges[(line_number, int(line_number))]['latency']
                elif (
                    line_number == int(line_number)
                    and 'mem_dep' in node
                    and self.dg.has_edge(node['mem_dep']['line_number'], line_number)
                ):
                    node['latency_cp'] += node['latency']
                else:
                    node['latency_cp'] += (
                        node['latency']
                        if 'latency_wo_load' not in node
                        else node['latency_wo_load']
                    )
            return [x for x in self.kernel if x['line_number'] in longest_path]
        else:
            # split to DAG
            raise NotImplementedError('Kernel is cyclic.')

    def get_loopcarried_dependencies(self):
        """
        Return all LCDs from kernel (after :func:`~KernelDG.check_for_loopcarried_dep` was run)
        """
        if nx.algorithms.dag.is_directed_acyclic_graph(self.dg):
            return self.loopcarried_deps
        else:
            # split to DAG
            raise NotImplementedError('Kernel is cyclic.')

    def find_depending(
        self, instruction_form, kernel, include_write=False, flag_dependencies=False
    ):
        """
        Find instructions in kernel depending on a given instruction form.

        :param dict instruction_form: instruction form to check for dependencies
        :param list kernel: kernel containing the instructions to check
        :param include_write: indicating if instruction ending the dependency chain should be included, defaults to `False`
        :type include_write: boolean, optional
        :param flag_dependencies: indicating if dependencies of flags should be considered, defaults to `False`
        :type flag_dependencies: boolean, optional
        :returns: iterator if all directly dependent instruction forms
        """
        if instruction_form.semantic_operands is None:
            return
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            if 'register' in dst:
                # Check for read of register until overwrite
                for instr_form in kernel:
                    if self.is_read(dst.register, instr_form):
                        yield instr_form
                        if self.is_written(dst.register, instr_form):
                            # operand in src_dst list
                            if include_write:
                                yield instr_form
                            break
                    elif self.is_written(dst.register, instr_form):
                        if include_write:
                            yield instr_form
                        break
            if 'flag' in dst and flag_dependencies:
                # Check for read of flag until overwrite
                for instr_form in kernel:
                    if self.is_read(dst.flag, instr_form):
                        yield instr_form
                        if self.is_written(dst.flag, instr_form):
                            # operand in src_dst list
                            if include_write:
                                yield instr_form
                            break
                    elif self.is_written(dst.flag, instr_form):
                        if include_write:
                            yield instr_form
                        break
            elif 'memory' in dst:
                # Check if base register is altered during memory access
                if 'pre_indexed' in dst.memory or 'post_indexed' in dst.memory:
                    # Check for read of base register until overwrite
                    for instr_form in kernel:
                        if self.is_read(dst.memory.base, instr_form):
                            instr_form['mem_dep'] = instruction_form
                            yield instr_form
                            if self.is_written(dst.memory.base, instr_form):
                                # operand in src_dst list
                                if include_write:
                                    instr_form['mem_dep'] = instruction_form
                                    yield instr_form
                                break
                        elif self.is_written(dst.memory.base, instr_form):
                            if include_write:
                                instr_form['mem_dep'] = instruction_form
                                yield instr_form
                            break

    def get_dependent_instruction_forms(self, instr_form=None, line_number=None):
        """
        Returns iterator
        """
        if not instr_form and not line_number:
            raise ValueError('Either instruction form or line_number required.')
        line_number = line_number if line_number else instr_form['line_number']
        if self.dg.has_node(line_number):
            return self.dg.successors(line_number)
        return iter([])

    def is_read(self, register, instruction_form):
        """Check if instruction form reads from given register"""
        is_read = False
        if instruction_form.semantic_operands is None:
            return is_read
        for src in chain(
            instruction_form.semantic_operands.source, instruction_form.semantic_operands.src_dst
        ):
            if 'register' in src:
                is_read = self.parser.is_reg_dependend_of(register, src.register) or is_read
            if 'flag' in src:
                is_read = self.parser.is_flag_dependend_of(register, src.flag) or is_read
            if 'memory' in src:
                if src.memory.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, src.memory.base) or is_read
                if src.memory.index is not None:
                    is_read = (
                        self.parser.is_reg_dependend_of(register, src.memory.index) or is_read
                    )
        # Check also if read in destination memory address
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            if 'memory' in dst:
                if dst.memory.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, dst.memory.base) or is_read
                if dst.memory.index is not None:
                    is_read = (
                        self.parser.is_reg_dependend_of(register, dst.memory.index) or is_read
                    )
        return is_read

    def is_written(self, register, instruction_form):
        """Check if instruction form writes in given register"""
        is_written = False
        if instruction_form.semantic_operands is None:
            return is_written
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            if 'register' in dst:
                is_written = self.parser.is_reg_dependend_of(register, dst.register) or is_written
            if 'flag' in dst:
                is_written = self.parser.is_flag_dependend_of(register, dst.flag) or is_written
            if 'memory' in dst:
                if 'pre_indexed' in dst.memory or 'post_indexed' in dst.memory:
                    is_written = (
                        self.parser.is_reg_dependend_of(register, dst.memory.base) or is_written
                    )
        # Check also for possible pre- or post-indexing in memory addresses
        for src in chain(
            instruction_form.semantic_operands.source, instruction_form.semantic_operands.src_dst
        ):
            if 'memory' in src:
                if 'pre_indexed' in src.memory or 'post_indexed' in src.memory:
                    is_written = (
                        self.parser.is_reg_dependend_of(register, src.memory.base) or is_written
                    )
        return is_written

    def export_graph(self, filepath=None):
        """
        Export graph with highlighted CP and LCDs as DOT file. Writes it to 'osaca_dg.dot'
        if no other path is given.

        :param filepath: path to write DOT file, defaults to None.
        :type filepath: str, optional
        """
        graph = copy.deepcopy(self.dg)
        cp = self.get_critical_path()
        cp_line_numbers = [x['line_number'] for x in cp]
        lcd = self.get_loopcarried_dependencies()
        lcd_line_numbers = {}
        for dep in lcd:
            lcd_line_numbers[dep] = [x['line_number'] for x in lcd[dep]['dependencies']]
        # add color scheme
        graph.graph['node'] = {'colorscheme': 'accent8'}
        graph.graph['edge'] = {'colorscheme': 'accent8'}

        # create LCD edges
        for dep in lcd_line_numbers:
            min_line_number = min(lcd_line_numbers[dep])
            max_line_number = max(lcd_line_numbers[dep])
            graph.add_edge(max_line_number, min_line_number)
            graph.edges[max_line_number, min_line_number]['latency'] = [
                x for x in lcd[dep]['dependencies'] if x['line_number'] == max_line_number
            ][0]['latency_lcd']

        # add label to edges
        for e in graph.edges:
            graph.edges[e]['label'] = graph.edges[e]['latency']

        # add CP values to graph
        for n in cp:
            graph.nodes[n['line_number']]['instruction_form']['latency_cp'] = n['latency_cp']

        # color CP and LCD
        for n in graph.nodes:
            if n in cp_line_numbers:
                # graph.nodes[n]['color'] = 1
                graph.nodes[n]['style'] = 'bold'
                graph.nodes[n]['penwidth'] = 4
            for col, dep in enumerate(lcd):
                if n in lcd_line_numbers[dep]:
                    if 'style' not in graph.nodes[n]:
                        graph.nodes[n]['style'] = 'filled'
                    else:
                        graph.nodes[n]['style'] += ',filled'
                    graph.nodes[n]['fillcolor'] = 2 + col

        # color edges
        for e in graph.edges:
            if (
                graph.nodes[e[0]]['instruction_form']['line_number'] in cp_line_numbers
                and graph.nodes[e[1]]['instruction_form']['line_number'] in cp_line_numbers
                and e[0] < e[1]
            ):
                bold_edge = True
                for i in range(e[0] + 1, e[1]):
                    if i in cp_line_numbers:
                        bold_edge = False
                if bold_edge:
                    graph.edges[e]['style'] = 'bold'
                    graph.edges[e]['penwidth'] = 3
            for dep in lcd_line_numbers:
                if (
                    graph.nodes[e[0]]['instruction_form']['line_number'] in lcd_line_numbers[dep]
                    and graph.nodes[e[1]]['instruction_form']['line_number']
                    in lcd_line_numbers[dep]
                ):
                    graph.edges[e]['color'] = graph.nodes[e[1]]['fillcolor']

        # rename node from [idx] to [idx mnemonic] and add shape
        mapping = {}
        for n in graph.nodes:
            if int(n) != n:
                mapping[n] = '{}: LOAD'.format(int(n))
                graph.nodes[n]['fontname'] = 'italic'
                graph.nodes[n]['fontsize'] = 11.0
            else:
                node = graph.nodes[n]['instruction_form']
                if node['instruction'] is not None:
                    mapping[n] = '{}: {}'.format(n, node['instruction'])
                else:
                    label = 'label' if node['label'] else None
                    label = 'directive' if node['directive'] else label
                    label = 'comment' if node['comment'] and label is None else label
                    mapping[n] = '{}: {}'.format(n, label)
                    graph.nodes[n]['fontname'] = 'italic'
                    graph.nodes[n]['fontsize'] = 11.0
                graph.nodes[n]['shape'] = 'rectangle'

        nx.relabel.relabel_nodes(graph, mapping, copy=False)
        if filepath:
            nx.drawing.nx_agraph.write_dot(graph, filepath)
        else:
            nx.drawing.nx_agraph.write_dot(graph, 'osaca_dg.dot')
