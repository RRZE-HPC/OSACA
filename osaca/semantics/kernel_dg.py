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
            dg.add_node(instruction_form["line_number"])
            dg.nodes[instruction_form["line_number"]]["instruction_form"] = instruction_form
            # add load as separate node if existent
            if (
                INSTR_FLAGS.HAS_LD in instruction_form["flags"]
                and INSTR_FLAGS.LD not in instruction_form["flags"]
            ):
                # add new node
                dg.add_node(instruction_form["line_number"] + 0.1)
                dg.nodes[instruction_form["line_number"] + 0.1][
                    "instruction_form"
                ] = instruction_form
                # and set LD latency as edge weight
                dg.add_edge(
                    instruction_form["line_number"] + 0.1,
                    instruction_form["line_number"],
                    latency=instruction_form["latency"] - instruction_form["latency_wo_load"],
                )
            for dep, dep_flags in self.find_depending(instruction_form, kernel[i + 1 :]):
                edge_weight = (
                    instruction_form["latency"]
                    if "latency_wo_load" not in instruction_form
                    else instruction_form["latency_wo_load"]
                )
                if "storeload_dep" in dep_flags:
                    edge_weight += self.model['store_to_load_forward_latency'] or 0
                dg.add_edge(
                    instruction_form["line_number"], dep["line_number"], latency=edge_weight
                )
                dg.nodes[dep["line_number"]]["instruction_form"] = dep
        return dg

    def check_for_loopcarried_dep(self, kernel):
        """
        Try to find loop-carried dependencies in given kernel.

        :param kernel: Parsed asm kernel with assigned semantic information
        :type kernel: list
        :returns: `dict` -- dependency dictionary with all cyclic LCDs
        """
        # increase line number for second kernel loop
        offset = max(1000, max([i.line_number for i in kernel]))
        first_line_no = kernel[0].line_number
        tmp_kernel = [] + kernel
        for orig_iform in kernel:
            temp_iform = copy.copy(orig_iform)
            temp_iform['line_number'] += offset
            tmp_kernel.append(temp_iform)
        # get dependency graph
        dg = self.create_DG(tmp_kernel)

        # build cyclic loop-carried dependencies
        loopcarried_deps = []
        paths = []
        for instr in kernel:
            paths += list(nx.algorithms.simple_paths.all_simple_paths(
                dg, instr.line_number, instr.line_number + offset))

        paths_set = set()
        for path in paths:
            lat_sum = 0.0
            # extend path by edge bound latencies (e.g., store-to-load latency)
            lat_path = []
            for i, (s, d) in enumerate(nx.utils.pairwise(path)):
                edge_lat = dg.edges[s, d]['latency']
                # map source node back to original line numbers
                if s >= offset:
                    s -= offset
                lat_path.append((s, edge_lat))
                lat_sum += edge_lat
            if d >= offset:
                d -= offset
            lat_path.sort()

            # Ignore duplicate paths which differ only in the root node
            if tuple(lat_path) in paths_set:
                continue
            paths_set.add(tuple(lat_path))

            loopcarried_deps.append((lat_sum, lat_path))
        loopcarried_deps.sort(reverse=True)

        # map lcd back to nodes
        loopcarried_deps_dict = {}
        for lat_sum, involved_lines in loopcarried_deps:
            loopcarried_deps_dict[involved_lines[0][0]] = {
                "root": self._get_node_by_lineno(involved_lines[0][0]),
                "dependencies": [(self._get_node_by_lineno(ln), lat) for ln, lat in involved_lines],
                "latency": lat_sum
            }

        return loopcarried_deps_dict

    def _get_node_by_lineno(self, lineno, kernel=None, all=False):
        """Return instruction form with line number ``lineno`` from  kernel"""
        if kernel is None:
            kernel = self.kernel
        result = [instr for instr in kernel if instr.line_number == lineno]
        if not all:
            return result[0]
        else:
            return result

    def get_critical_path(self):
        """Find and return critical path after the creation of a directed graph."""
        if nx.algorithms.dag.is_directed_acyclic_graph(self.dg):
            longest_path = nx.algorithms.dag.dag_longest_path(self.dg, weight="latency")
            for line_number in longest_path:
                self._get_node_by_lineno(int(line_number))["latency_cp"] = 0
            # add LD latency to instruction
            for line_number in longest_path:
                node = self._get_node_by_lineno(int(line_number))
                if line_number != int(line_number) and int(line_number) in longest_path:
                    node["latency_cp"] += self.dg.edges[(line_number, int(line_number))]["latency"]
                elif (
                    line_number == int(line_number)
                    and "mem_dep" in node
                    and self.dg.has_edge(node["mem_dep"]["line_number"], line_number)
                ):
                    node["latency_cp"] += node["latency"]
                elif (
                    line_number == int(line_number)
                    and "storeload_dep" in node
                    and self.dg.has_edge(node["storeload_dep"]["line_number"], line_number)
                ):
                    node["latency_cp"] += self.model['store_to_load_forward_latency'] or 0
                else:
                    node["latency_cp"] += (
                        node["latency"]
                        if "latency_wo_load" not in node
                        else node["latency_wo_load"]
                    )
            return [x for x in self.kernel if x["line_number"] in longest_path]
        else:
            # split to DAG
            raise NotImplementedError("Kernel is cyclic.")

    def get_loopcarried_dependencies(self):
        """
        Return all LCDs from kernel (after :func:`~KernelDG.check_for_loopcarried_dep` was run)
        """
        if nx.algorithms.dag.is_directed_acyclic_graph(self.dg):
            return self.loopcarried_deps
        else:
            # split to DAG
            raise NotImplementedError("Kernel is cyclic.")

    def find_depending(
        self, instruction_form, instructions, flag_dependencies=False
    ):
        """
        Find instructions in `instructions` depending on a given instruction form's results.

        :param dict instruction_form: instruction form to check for dependencies
        :param list instructions: instructions to check
        :param flag_dependencies: indicating if dependencies of flags should be considered,
                                  defaults to `False`
        :type flag_dependencies: boolean, optional
        :returns: iterator if all directly dependent instruction forms and according flags
        """
        if instruction_form.semantic_operands is None:
            return
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            # Check for sources, until overwritten
            for i, instr_form in enumerate(instructions):
                # TODO detect dependency breaking instructions
                if "register" in dst:
                    # read of register
                    if self.is_read(dst.register, instr_form):
                        yield instr_form, []
                    # write to register -> abort
                    if self.is_written(dst.register, instr_form):
                        break
                if "flag" in dst and flag_dependencies:
                    # read of flag
                    if self.is_read(dst.flag, instr_form):
                        yield instr_form, []
                    # write to flag -> abort
                    if self.is_written(dst.flag, instr_form):
                        break
                if "memory" in dst:
                    # base register is altered during memory access
                    if "pre_indexed" in dst.memory or "post_indexed" in dst.memory:
                        # Check for read of base register until overwrite
                        if self.is_read(dst.memory.base, instr_form):
                            instr_form["mem_dep"] = instruction_form
                            yield instr_form, ["mem_dep"]
                            if self.is_written(dst.memory.base, instr_form):
                                break
                        if self.is_written(dst.memory.base, instr_form):
                            break
                    # TODO record register changes
                    #      (e.g., mov, leaadd, sub, inc, dec) in instructions[:i] 
                    #      and pass to is_memload and is_memstore to consider relevance.
                    # load from same location (presumed)
                    if self.is_memload(dst.memory, instr_form):
                        instr_form["storeload_dep"] = instruction_form
                        yield instr_form, ["storeload_dep"]
                    # store to same location (presumed)
                    if self.is_memstore(dst.memory, instr_form):
                        break

    def get_dependent_instruction_forms(self, instr_form=None, line_number=None):
        """
        Returns iterator
        """
        if not instr_form and not line_number:
            raise ValueError("Either instruction form or line_number required.")
        line_number = line_number if line_number else instr_form["line_number"]
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
            if "register" in src:
                is_read = self.parser.is_reg_dependend_of(register, src.register) or is_read
            if "flag" in src:
                is_read = self.parser.is_flag_dependend_of(register, src.flag) or is_read
            if "memory" in src:
                if src.memory.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, src.memory.base) or is_read
                if src.memory.index is not None:
                    is_read = self.parser.is_reg_dependend_of(register, src.memory.index) or is_read
        # Check also if read in destination memory address
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            if "memory" in dst:
                if dst.memory.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, dst.memory.base) or is_read
                if dst.memory.index is not None:
                    is_read = self.parser.is_reg_dependend_of(register, dst.memory.index) or is_read
        return is_read

    def is_memload(self, mem, instruction_form):
        """Check if instruction form loads from given location, assuming unchanged registers"""
        is_load = False
        if instruction_form.semantic_operands is None:
            return is_load
        for src in chain(
            instruction_form.semantic_operands.source, instruction_form.semantic_operands.src_dst
        ):
            if "memory" in src:
                is_load = mem == src["memory"] or is_load
        return is_load

    def is_written(self, register, instruction_form):
        """Check if instruction form writes in given register"""
        is_written = False
        if instruction_form.semantic_operands is None:
            return is_written
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            if "register" in dst:
                is_written = self.parser.is_reg_dependend_of(register, dst.register) or is_written
            if "flag" in dst:
                is_written = self.parser.is_flag_dependend_of(register, dst.flag) or is_written
            if "memory" in dst:
                if "pre_indexed" in dst.memory or "post_indexed" in dst.memory:
                    is_written = (
                        self.parser.is_reg_dependend_of(register, dst.memory.base) or is_written
                    )
        # Check also for possible pre- or post-indexing in memory addresses
        for src in chain(
            instruction_form.semantic_operands.source, instruction_form.semantic_operands.src_dst
        ):
            if "memory" in src:
                if "pre_indexed" in src.memory or "post_indexed" in src.memory:
                    is_written = (
                        self.parser.is_reg_dependend_of(register, src.memory.base) or is_written
                    )
        return is_written

    def is_memstore(self, mem, instruction_form):
        """Check if instruction form stores to given location, assuming unchanged registers"""
        is_store = False
        if instruction_form.semantic_operands is None:
            return is_store
        for dst in chain(
            instruction_form.semantic_operands.destination,
            instruction_form.semantic_operands.src_dst,
        ):
            if "memory" in dst:
                is_store = mem == dst["memory"] or is_store
        return is_store

    def export_graph(self, filepath=None):
        """
        Export graph with highlighted CP and LCDs as DOT file. Writes it to 'osaca_dg.dot'
        if no other path is given.

        :param filepath: path to write DOT file, defaults to None.
        :type filepath: str, optional
        """
        graph = copy.deepcopy(self.dg)
        cp = self.get_critical_path()
        cp_line_numbers = [x["line_number"] for x in cp]
        lcd = self.get_loopcarried_dependencies()
        lcd_line_numbers = {}
        for dep in lcd:
            lcd_line_numbers[dep] = [x["line_number"] for x, lat in lcd[dep]["dependencies"]]
        # add color scheme
        graph.graph["node"] = {"colorscheme": "accent8"}
        graph.graph["edge"] = {"colorscheme": "accent8"}

        # create LCD edges
        for dep in lcd_line_numbers:
            min_line_number = min(lcd_line_numbers[dep])
            max_line_number = max(lcd_line_numbers[dep])
            graph.add_edge(max_line_number, min_line_number)
            graph.edges[max_line_number, min_line_number]["latency"] = [
                lat for x, lat in lcd[dep]["dependencies"] if x["line_number"] == max_line_number
            ]

        # add label to edges
        for e in graph.edges:
            graph.edges[e]["label"] = graph.edges[e]["latency"]

        # add CP values to graph
        for n in cp:
            graph.nodes[n["line_number"]]["instruction_form"]["latency_cp"] = n["latency_cp"]

        # color CP and LCD
        for n in graph.nodes:
            if n in cp_line_numbers:
                # graph.nodes[n]['color'] = 1
                graph.nodes[n]["style"] = "bold"
                graph.nodes[n]["penwidth"] = 4
            for col, dep in enumerate(lcd):
                if n in lcd_line_numbers[dep]:
                    if "style" not in graph.nodes[n]:
                        graph.nodes[n]["style"] = "filled"
                    else:
                        graph.nodes[n]["style"] += ",filled"
                    graph.nodes[n]["fillcolor"] = 2 + col

        # color edges
        for e in graph.edges:
            if (
                graph.nodes[e[0]]["instruction_form"]["line_number"] in cp_line_numbers
                and graph.nodes[e[1]]["instruction_form"]["line_number"] in cp_line_numbers
                and e[0] < e[1]
            ):
                bold_edge = True
                for i in range(e[0] + 1, e[1]):
                    if i in cp_line_numbers:
                        bold_edge = False
                if bold_edge:
                    graph.edges[e]["style"] = "bold"
                    graph.edges[e]["penwidth"] = 3
            for dep in lcd_line_numbers:
                if (
                    graph.nodes[e[0]]["instruction_form"]["line_number"] in lcd_line_numbers[dep]
                    and graph.nodes[e[1]]["instruction_form"]["line_number"]
                    in lcd_line_numbers[dep]
                ):
                    graph.edges[e]["color"] = graph.nodes[e[1]]["fillcolor"]

        # rename node from [idx] to [idx mnemonic] and add shape
        mapping = {}
        for n in graph.nodes:
            if int(n) != n:
                mapping[n] = "{}: LOAD".format(int(n))
                graph.nodes[n]["fontname"] = "italic"
                graph.nodes[n]["fontsize"] = 11.0
            else:
                node = graph.nodes[n]["instruction_form"]
                if node["instruction"] is not None:
                    mapping[n] = "{}: {}".format(n, node["instruction"])
                else:
                    label = "label" if node["label"] else None
                    label = "directive" if node["directive"] else label
                    label = "comment" if node["comment"] and label is None else label
                    mapping[n] = "{}: {}".format(n, label)
                    graph.nodes[n]["fontname"] = "italic"
                    graph.nodes[n]["fontsize"] = 11.0
                graph.nodes[n]["shape"] = "rectangle"

        nx.relabel.relabel_nodes(graph, mapping, copy=False)
        if filepath:
            nx.drawing.nx_agraph.write_dot(graph, filepath)
        else:
            nx.drawing.nx_agraph.write_dot(graph, "osaca_dg.dot")
