#!/usr/bin/env python3

import copy
from enum import Enum
import time
from itertools import chain, groupby
from multiprocessing import Manager, Process, cpu_count

import networkx as nx
from osaca.semantics import INSTR_FLAGS, ArchSemantics, MachineModel
from osaca.parser.instruction_form import InstructionForm
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.flag import FlagOperand


class KernelDG(nx.DiGraph):
    # threshold for checking dependency graph sequential or in parallel
    INSTRUCTION_THRESHOLD = 50

    class ReadKind(Enum):
        NOT_A_READ = 0
        READ_FOR_LOAD = 1
        OTHER_READ = 2

    def __init__(
        self,
        parsed_kernel,
        parser,
        hw_model: MachineModel,
        semantics: ArchSemantics,
        timeout=10,
        flag_dependencies=False,
    ):
        self.timed_out = False
        self.kernel = parsed_kernel
        self.parser = parser
        self.model = hw_model
        self.arch_sem = semantics
        self.dg = self.create_DG(self.kernel, flag_dependencies)
        self.loopcarried_deps = self.check_for_loopcarried_dep(
            self.kernel, timeout, flag_dependencies
        )

    @classmethod
    def _extend_path(cls, dst_list, kernel, dg, offset):
        for instr in kernel:
            generator_path = nx.algorithms.simple_paths.all_simple_paths(
                dg, instr.line_number, instr.line_number + offset
            )
            tmp_list = list(generator_path)
            dst_list.extend(tmp_list)
        # print('Thread [{}-{}] done'.format(kernel[0]['line_number'], kernel[-1]['line_number']))

    @staticmethod
    def get_load_line_number(line_number):
        # The line number of the load must be less than the line number of the instruction.  The
        # offset is irrelevant, but it must be a machine number with trailing zeroes to avoid silly
        # rounding issues.
        return line_number - 0.125

    @staticmethod
    def is_load_line_number(line_number):
        return line_number != int(line_number)

    @staticmethod
    def get_real_line_number(line_number):
        return (
            int(line_number + 0.125) if KernelDG.is_load_line_number(line_number) else line_number
        )

    def create_DG(self, kernel, flag_dependencies=False):
        """
        Create directed graph from given kernel

        :param kernel: Parsed asm kernel with assigned semantic information
        :type kerne: list
        :param flag_dependencies: indicating if dependencies of flags should be considered,
                                  defaults to `False`
        :type flag_dependencies: boolean, optional
        :returns: :class:`~nx.DiGraph` -- directed graph object
        """
        # Go through kernel instruction forms and add them as nodes of the graph.  Create a LOAD
        # node for instructions that include a memory reference.
        dg = nx.DiGraph()
        loads = {}
        for i, instruction_form in enumerate(kernel):
            dg.add_node(instruction_form.line_number)
            dg.nodes[instruction_form.line_number]["instruction_form"] = instruction_form
            # add load as separate node if existent
            if (
                INSTR_FLAGS.HAS_LD in instruction_form.flags
                and INSTR_FLAGS.LD not in instruction_form.flags
            ):
                # add new node
                load_line_number = KernelDG.get_load_line_number(instruction_form.line_number)
                loads[instruction_form.line_number] = load_line_number
                dg.add_node(load_line_number)
                dg.nodes[load_line_number]["instruction_form"] = InstructionForm(
                    mnemonic="_LOAD_", line=instruction_form.line, line_number=load_line_number
                )
                # and set LD latency as edge weight
                dg.add_edge(
                    load_line_number,
                    instruction_form.line_number,
                    latency=instruction_form.latency - instruction_form.latency_wo_load,
                )

        # 1. find edges (to dependend further instruction)
        # 2. get LT value and set as edge weight
        for i, instruction_form in enumerate(kernel):
            for dep, dep_flags in self.find_depending(
                instruction_form, kernel[i + 1 :], flag_dependencies
            ):
                # print(instruction_form.line_number,"\t",dep.line_number,"\n")
                edge_weight = (
                    instruction_form.latency
                    if "mem_dep" in dep_flags or instruction_form.latency_wo_load is None
                    else instruction_form.latency_wo_load
                )
                if "storeload_dep" in dep_flags and self.model is not None:
                    edge_weight += self.model.get("store_to_load_forward_latency", 0)
                if "p_indexed" in dep_flags and self.model is not None:
                    edge_weight = self.model.get("p_index_latency", 1)
                if "for_load" in dep_flags and self.model is not None and dep.line_number in loads:
                    dg.add_edge(
                        instruction_form.line_number,
                        loads[dep.line_number],
                        latency=edge_weight,
                    )
                else:
                    dg.add_edge(
                        instruction_form.line_number,
                        dep.line_number,
                        latency=edge_weight,
                    )

                dg.nodes[dep.line_number]["instruction_form"] = dep
        return dg

    def check_for_loopcarried_dep(self, kernel, timeout=10, flag_dependencies=False):
        """
        Try to find loop-carried dependencies in given kernel.

        :param kernel: Parsed asm kernel with assigned semantic information
        :type kernel: list
        :param timeout: Timeout in seconds for parallel execution, defaults
                                    to `10`. Set to `0` for no timeout
        :type timeout: int
        :returns: `dict` -- dependency dictionary with all cyclic LCDs
        """
        # increase line number for second kernel loop
        offset = max(1000, max([i.line_number for i in kernel]))
        tmp_kernel = [] + kernel
        for orig_iform in kernel:
            temp_iform = copy.copy(orig_iform)
            temp_iform.line_number += offset
            tmp_kernel.append(temp_iform)
        # get dependency graph
        dg = self.create_DG(tmp_kernel, flag_dependencies)

        # build cyclic loop-carried dependencies
        loopcarried_deps = []
        all_paths = []

        klen = len(kernel)
        if klen >= self.INSTRUCTION_THRESHOLD:
            # parallel execution with static scheduling
            num_cores = cpu_count()
            workload = int((klen - 1) / num_cores) + 1
            starts = [tid * workload for tid in range(num_cores)]
            ends = [min((tid + 1) * workload, klen) for tid in range(num_cores)]
            instrs = [kernel[s:e] for s, e in zip(starts, ends)]
            with Manager() as manager:
                all_paths = manager.list()
                processes = [
                    Process(
                        target=KernelDG._extend_path,
                        args=(all_paths, instr_section, dg, offset),
                    )
                    for instr_section in instrs
                ]
                for p in processes:
                    p.start()
                if timeout == -1:
                    # no timeout
                    for p in processes:
                        p.join()
                else:
                    start_time = time.time()
                    while time.time() - start_time <= timeout:
                        if any(p.is_alive() for p in processes):
                            time.sleep(0.2)
                        else:
                            # all procs done
                            for p in processes:
                                p.join()
                            break
                    else:
                        self.timed_out = True
                        # terminate running processes
                        for p in processes:
                            if p.is_alive():
                                p.kill()
                            p.join()
                all_paths = list(all_paths)
        else:
            # sequential execution to avoid overhead when analyzing smaller kernels
            for instr in kernel:
                all_paths.extend(
                    nx.algorithms.simple_paths.all_simple_paths(
                        dg, instr.line_number, instr.line_number + offset
                    )
                )

        paths_set = set()
        for path in all_paths:
            lat_sum = 0.0
            # extend path by edge bound latencies (e.g., store-to-load latency)
            lat_path = []
            for s, d in nx.utils.pairwise(path):
                edge_lat = dg.edges[s, d]["latency"]
                # map source node back to original line numbers
                if s > offset:
                    s -= offset
                lat_path.append((s, edge_lat))
                lat_sum += edge_lat
            if d > offset:
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
            dict_key = "-".join([str(il[0]) for il in involved_lines])
            loopcarried_deps_dict[dict_key] = {
                "root": self._get_node_by_lineno(dg, involved_lines[0][0]),
                "dependencies": [
                    (self._get_node_by_lineno(dg, ln), lat) for ln, lat in involved_lines
                ],
                "latency": lat_sum,
            }
        return loopcarried_deps_dict

    def _get_node_by_lineno(self, dg, lineno):
        """Return instruction form with line number ``lineno`` from  dg"""
        return dg.nodes[lineno]["instruction_form"]

    def get_critical_path(self):
        """Find and return critical path after the creation of a directed graph."""
        max_latency_instr = max(self.kernel, key=lambda k: k.latency)
        if nx.algorithms.dag.is_directed_acyclic_graph(self.dg):
            longest_path = nx.algorithms.dag.dag_longest_path(self.dg, weight="latency")
            # TODO verify that we can remove the next two lince due to earlier initialization
            for line_number in longest_path:
                self._get_node_by_lineno(self.dg, line_number).latency_cp = 0
            # set cp latency to instruction
            path_latency = 0.0
            for s, d in nx.utils.pairwise(longest_path):
                node = self._get_node_by_lineno(self.dg, s)
                node.latency_cp = self.dg.edges[(s, d)]["latency"]
                path_latency += node.latency_cp
            # add latency for last instruction
            node = self._get_node_by_lineno(self.dg, longest_path[-1])
            node.latency_cp = node.latency
            if max_latency_instr.latency > path_latency:
                max_latency_instr.latency_cp = float(max_latency_instr.latency)
                return [max_latency_instr]
            else:
                return [self._get_node_by_lineno(self.dg, x) for x in longest_path]
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

    def find_depending(self, instruction_form, instructions, flag_dependencies=False):
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
            instruction_form.semantic_operands["destination"],
            instruction_form.semantic_operands["src_dst"],
        ):
            # TODO instructions before must be considered as well, if they update registers
            # not used by insruction_form. E.g., validation/build/A64FX/gcc/O1/gs-2d-5pt.marked.s
            register_changes = self._update_reg_changes(instruction_form)
            # print("FROM", instruction_form.line, register_changes)
            for i, instr_form in enumerate(instructions):
                self._update_reg_changes(instr_form, register_changes)
                # print("  TO", instr_form.line, register_changes)
                if isinstance(dst, RegisterOperand):
                    # read of register
                    read_kind = self._read_kind(dst, instr_form)
                    if read_kind != KernelDG.ReadKind.NOT_A_READ:
                        dep_flags = []
                        if (
                            dst.pre_indexed
                            or dst.post_indexed
                            or (isinstance(dst.post_indexed, dict))
                        ):
                            dep_flags = ["p_indexed"]
                        if read_kind == KernelDG.ReadKind.READ_FOR_LOAD:
                            dep_flags += ["for_load"]
                        yield instr_form, dep_flags
                    # write to register -> abort
                    if self.is_written(dst, instr_form):
                        break
                if isinstance(dst, FlagOperand) and flag_dependencies:
                    # read of flag
                    if self.is_read(dst, instr_form):
                        yield instr_form, []
                    # write to flag -> abort
                    if self.is_written(dst, instr_form):
                        break
                if isinstance(dst, MemoryOperand):
                    # base register is altered during memory access
                    if dst.pre_indexed:
                        if self.is_written(dst.base, instr_form):
                            break
                    # if dst.memory.base:
                    #    if self.is_read(dst.memory.base, instr_form):
                    #        yield instr_form, []
                    # if dst.memory.index:
                    #    if self.is_read(dst.memory.index, instr_form):
                    #        yield instr_form, []
                    if dst.post_indexed:
                        # Check for read of base register until overwrite
                        if self.is_written(dst.base, instr_form):
                            break
                    # TODO record register changes
                    #      (e.g., mov, leaadd, sub, inc, dec) in instructions[:i]
                    #      and pass to is_memload and is_memstore to consider relevance.
                    # load from same location (presumed)
                    if self.is_memload(dst, instr_form, register_changes):
                        yield instr_form, ["storeload_dep"]
                    # store to same location (presumed)
                    if self.is_memstore(dst, instr_form, register_changes):
                        break
                self._update_reg_changes(instr_form, register_changes, only_postindexed=True)

    def _update_reg_changes(self, iform, reg_state=None, only_postindexed=False):
        if self.arch_sem is None:
            # This analysis requires semenatics to be available
            return {}
        if reg_state is None:
            reg_state = {}
        for reg, change in self.arch_sem.get_reg_changes(iform, only_postindexed).items():
            if change is None or reg_state.get(reg, {}) is None:
                reg_state[reg] = None
            else:
                reg_state.setdefault(reg, {"name": reg, "value": 0})
                if change["name"] != reg:
                    # renaming occured, ovrwrite value with up-to-now change of source register
                    reg_state[reg]["name"] = change["name"]
                    src_reg_state = reg_state.get(change["name"], {"value": 0})
                    if src_reg_state is None:
                        # original register's state was changed beyond reconstruction
                        reg_state[reg] = None
                        continue
                    reg_state[reg]["value"] = src_reg_state["value"]
                reg_state[reg]["value"] += change["value"]
        return reg_state

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

    def _read_kind(self, register, instruction_form):
        """Check if instruction form reads from given register.  Returns a ReadKind."""
        is_read = False
        for_load = False
        if instruction_form.semantic_operands is None:
            return KernelDG.ReadKind.NOT_A_READ
        for src in chain(
            instruction_form.semantic_operands["source"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(src, RegisterOperand):
                is_read = self.parser.is_reg_dependend_of(register, src) or is_read
            if isinstance(src, FlagOperand):
                is_read = self.parser.is_flag_dependend_of(register, src) or is_read
            if isinstance(src, MemoryOperand):
                is_memory_read = False
                if src.base is not None:
                    is_memory_read = self.parser.is_reg_dependend_of(register, src.base)
                if src.index is not None and isinstance(src.index, RegisterOperand):
                    is_memory_read = (
                        self.parser.is_reg_dependend_of(register, src.index) or is_memory_read
                    )
                for_load = is_memory_read
                is_read = is_read or is_memory_read
        # Check also if read in destination memory address
        for dst in chain(
            instruction_form.semantic_operands["destination"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(dst, MemoryOperand):
                if dst.base is not None:
                    is_read = self.parser.is_reg_dependend_of(register, dst.base) or is_read
                if dst.index is not None:
                    is_read = self.parser.is_reg_dependend_of(register, dst.index) or is_read
        if is_read:
            if for_load:
                return KernelDG.ReadKind.READ_FOR_LOAD
            else:
                return KernelDG.ReadKind.OTHER_READ
        else:
            return KernelDG.ReadKind.NOT_A_READ

    def is_read(self, register, instruction_form):
        return self._read_kind(register, instruction_form) != KernelDG.ReadKind.NOT_A_READ

    def is_memload(self, mem, instruction_form, register_changes={}):
        """Check if instruction form loads from given location, assuming register_changes"""
        if instruction_form.semantic_operands is None:
            return False
        for src in chain(
            instruction_form.semantic_operands["source"],
            instruction_form.semantic_operands["src_dst"],
        ):
            # Here we check for mem dependecies only
            if not isinstance(src, MemoryOperand):
                continue
            # src = src.memory

            # determine absolute address change
            addr_change = 0
            if isinstance(src.offset, ImmediateOperand) and src.offset.value is not None:
                addr_change += src.offset.value
            if isinstance(mem.offset, ImmediateOperand) and mem.offset.value is not None:
                addr_change -= mem.offset.value
            if mem.base and src.base:
                base_change = register_changes.get(
                    (src.base.prefix if src.base.prefix is not None else "") + src.base.name,
                    {
                        "name": (src.base.prefix if src.base.prefix is not None else "")
                        + src.base.name,
                        "value": 0,
                    },
                )
                if base_change is None:
                    # Unknown change occurred
                    continue
                if (
                    mem.base.prefix
                    if mem.base.prefix is not None
                    else "" + mem.base.name != base_change["name"]
                ):
                    # base registers do not match
                    continue
                addr_change += base_change["value"]
            elif mem.base or src.base:
                # base registers do not match
                continue
            if mem.index and src.index:
                index_change = register_changes.get(
                    (src.index.prefix if src.index.prefix is not None else "") + src.index.name,
                    {
                        "name": (src.index.prefix if src.index.prefix is not None else "")
                        + src.index.name,
                        "value": 0,
                    },
                )
                if index_change is None:
                    # Unknown change occurred
                    continue
                if mem.scale != src.scale:
                    # scale factors do not match
                    continue
                if (
                    mem.index.prefix
                    if mem.index.prefix is not None
                    else "" + mem.index.name != index_change["name"]
                ):
                    # index registers do not match
                    continue
                addr_change += index_change["value"] * src.scale
            elif mem.index or src.index:
                # index registers do not match
                continue
            # if instruction_form.line_number == 3:
            if addr_change == 0:
                return True
        return False

    def is_written(self, register, instruction_form):
        """Check if instruction form writes in given register"""
        is_written = False
        if instruction_form.semantic_operands is None:
            return is_written
        for dst in chain(
            instruction_form.semantic_operands["destination"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(dst, RegisterOperand):
                is_written = self.parser.is_reg_dependend_of(register, dst) or is_written
            if isinstance(dst, FlagOperand):
                is_written = self.parser.is_flag_dependend_of(register, dst) or is_written
            if isinstance(dst, MemoryOperand):
                if dst.pre_indexed or dst.post_indexed:
                    is_written = self.parser.is_reg_dependend_of(register, dst.base) or is_written
        # Check also for possible pre- or post-indexing in memory addresses
        for src in chain(
            instruction_form.semantic_operands["source"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(src, MemoryOperand):
                if src.pre_indexed or src.post_indexed:
                    is_written = self.parser.is_reg_dependend_of(register, src.base) or is_written
        return is_written

    def is_memstore(self, mem, instruction_form, register_changes={}):
        """Check if instruction form stores to given location, assuming unchanged registers"""
        is_store = False
        if instruction_form.semantic_operands is None:
            return is_store
        for dst in chain(
            instruction_form.semantic_operands["destination"],
            instruction_form.semantic_operands["src_dst"],
        ):
            if isinstance(dst, MemoryOperand):
                is_store = mem == dst or is_store
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
        cp_line_numbers = [x.line_number for x in cp]
        lcd = self.get_loopcarried_dependencies()
        lcd_line_numbers = {}
        for dep in lcd:
            lcd_line_numbers[dep] = [x.line_number for x, lat in lcd[dep]["dependencies"]]

        # create LCD edges
        for dep in lcd_line_numbers:
            min_line_number = min(lcd_line_numbers[dep])
            max_line_number = max(lcd_line_numbers[dep])
            graph.add_edge(min_line_number, max_line_number, dir="back")
            graph.edges[min_line_number, max_line_number]["latency"] = [
                lat for x, lat in lcd[dep]["dependencies"] if x.line_number == max_line_number
            ]

        # add label to edges
        for e in graph.edges:
            graph.edges[e]["label"] = graph.edges[e]["latency"]

        # add CP values to graph
        for n in cp:
            graph.nodes[n.line_number]["instruction_form"].latency_cp = n.latency_cp

        # Make the critical path bold.
        for n in graph.nodes:
            if n in cp_line_numbers:
                # graph.nodes[n]['color'] = 1
                graph.nodes[n]["style"] = "bold"
                graph.nodes[n]["penwidth"] = 4

        # Make critical path edges bold.
        for u, v in zip(cp_line_numbers[:-1], cp_line_numbers[1:]):
            graph.edges[u, v]["style"] = "bold"
            graph.edges[u, v]["penwidth"] = 3

        # Color the cycles created by loop-carried dependencies, longest first, never recoloring
        # any node or edge, so that the longest LCD and most long chains that are involved in the
        # loop are legible.
        lcd_by_latencies = sorted(
            (
                (latency, list(deps))
                for latency, deps in groupby(lcd, lambda dep: lcd[dep]["latency"])
            ),
            reverse=True,
        )
        node_colors = {}
        edge_colors = {}
        colors_used = 0
        for i, (latency, deps) in enumerate(lcd_by_latencies):
            color = None
            for dep in deps:
                path = lcd_line_numbers[dep]
                for n in path:
                    if n not in node_colors:
                        if not color:
                            color = colors_used + 1
                            colors_used += 1
                        node_colors[n] = color
                for u, v in zip(path, path[1:] + [path[0]]):
                    if (u, v) not in edge_colors:
                        # Don’t introduce a color just for an edge.
                        if not color:
                            color = colors_used
                        edge_colors[u, v] = color
        max_color = min(11, colors_used)
        colorscheme = f"spectral{max(3, max_color)}"
        graph.graph["node"] = {"colorscheme": colorscheme}
        graph.graph["edge"] = {"colorscheme": colorscheme}
        for n, color in node_colors.items():
            if "style" not in graph.nodes[n]:
                graph.nodes[n]["style"] = "filled"
            else:
                graph.nodes[n]["style"] += ",filled"
            graph.nodes[n]["fillcolor"] = color
            if (max_color >= 4 and color in (1, max_color)) or (
                max_color >= 10 and color in (1, 2, max_color - 1, max_color)
            ):
                graph.nodes[n]["fontcolor"] = "white"
        for (u, v), color in edge_colors.items():
            # The backward edge of the cycle is represented as the corresponding forward
            # edge with the attribute dir=back.
            edge = graph.edges[u, v] if (u, v) in graph.edges else graph.edges[v, u]
            edge["color"] = color

        # rename node from [idx] to [idx mnemonic] and add shape
        mapping = {}
        for n in graph.nodes:
            node = graph.nodes[n]["instruction_form"]
            if node.mnemonic is not None:
                mapping[n] = "{}: {}".format(KernelDG.get_real_line_number(n), node.mnemonic)
            else:
                label = "label" if node.label is not None else None
                label = "directive" if node.directive is not None else label
                label = "comment" if node.comment is not None and label is None else label
                mapping[n] = "{}: {}".format(n, label)
                graph.nodes[n]["fontname"] = "italic"
                graph.nodes[n]["fontsize"] = 11.0
            if not KernelDG.is_load_line_number(n):
                graph.nodes[n]["shape"] = "rectangle"

        nx.relabel.relabel_nodes(graph, mapping, copy=False)
        if filepath:
            nx.drawing.nx_agraph.write_dot(graph, filepath)
        else:
            nx.drawing.nx_agraph.write_dot(graph, "osaca_dg.dot")
