#!/usr/bin/env python3

import sys
import os
import math
import ast
from operator import add
import pandas as pd

from osaca.param import Register, MemAddr
#from param import Register, MemAddr


class Scheduler(object):
    arch_dict = {
        # Intel
        'NHM': 5, 'WSM': 5,  # Nehalem, Westmere
        'SNB': 6, 'IVB': 6,  # Sandy Bridge, Ivy Bridge
        'HSW': 8, 'BDW': 8,  # Haswell, Broadwell
        'SKL': 8, 'SKX': 8,  # Skylake(-X)
        'KBL': 8, 'CFL': 8,  # Kaby Lake, Coffee Lake
        # AMD
        'ZEN': 10,  # Zen/Ryzen/EPYC
    }
    arch_pipeline_ports = {
        'NHM': ['0DV'], 'WSM': ['0DV'],
        'SNB': ['0DV'], 'IVB': ['0DV'],
        'HSW': ['0DV'], 'BDW': ['0DV'],
        'SKL': ['0DV'], 'SKX': ['0DV'],
        'KBL': ['0DV'], 'CFL': ['0DV'],
        'ZEN': ['3DV'],}
    # content of most inner list in instrList: instr, operand(s), instr form
    df = None  # type: DataFrame
    # for parallel ld/st in archs with 1 st/cy and >1 ld/cy, able to do 1 st and 1 ld in 1cy
    ld_ports = None  # type: list<int>
    # enable flag for parallel ld/st
    en_par_ldst = False  # type: boolean

    def __init__(self, arch, instruction_list):
        arch = arch.upper()
        try:
            self.ports = self.arch_dict[arch]
        except KeyError:
            print('Architecture not supported for EU scheduling.', file=sys.stderr)
            sys.exit(1)
        # check for parallel ld/st in a cycle
        if arch == 'ZEN':
            self.en_par_ldst = True
            self.ld_ports = [9, 10]
        # check for DV port
        self.pipeline_ports = self.arch_pipeline_ports.get(arch, [])
        self.instrList = instruction_list
        # curr_dir = os.path.realpath(__file__)[:-11]
        osaca_dir = os.path.expanduser('~/.osaca/')
        self.df = pd.read_csv(osaca_dir + 'data/' + arch.lower() + '_data.csv', quotechar='"',
                              converters={'ports': ast.literal_eval})

    def new_schedule(self, machine_readable=False):
        """
        Schedule Instruction Form list and calculate port bindings.

        Parameters
        ----------
        machine_readable : bool
            Boolean for indicating if the return value should be human readable (if False) or 
            machine readable (if True)

        Returns
        -------
        (str, [float, ...]) or ([[float, ...], ...], [float, ...])
            A tuple containing the output of the schedule as string (if machine_readable is not
            given or False) or as list of lists (if machine_readable is True) and the port bindings
            as list of float.
        """
        sched = self.get_head()
        # Initialize ports
        # Add DV port, if it is existing
        occ_ports = [[0] * (self.ports + len(self.pipeline_ports)) for x in range(len(self.instrList))]
        port_bndgs = [0] * (self.ports + len(self.pipeline_ports))
        # Store instruction counter for parallel ld/st
        par_ldst = 0
        # Count the number of store instr if we schedule for an architecture with par ld/st
        if self.en_par_ldst:
            for i, instrForm in enumerate(self.instrList):
                if (isinstance(instrForm[1], MemAddr) and len(instrForm) > 3
                        and not instrForm[0].startswith('cmp')):
                    # print('({}, {}) is st --> par_ldst = {}'.format(i, instrForm[0], par_ldst + 1))
                    par_ldst += 1
        # Check if there's a port occupation stored in the CSV, otherwise leave the
        # occ_port list item empty
        for i, instrForm in enumerate(self.instrList):
            search_string = instrForm[0] + self.get_operand_suffix(instrForm)
            try:
                entry = self.df.loc[lambda df, sStr=search_string: df.instr == sStr]
                tup = entry.ports.values[0]
                if len(tup) == 1 and tup[0] == -1:
                    raise IndexError()
            except IndexError:
                # Instruction form not in CSV
                if instrForm[0][:3] == 'nop':
                    sched += self.format_port_occupation_line(occ_ports[i], '* ' + instrForm[-1])
                elif instrForm[0] == 'DIRECTIVE':
                    sched += self.format_port_occupation_line(occ_ports[i], '* ' + instrForm[-1])
                else:
                    sched += self.format_port_occupation_line(occ_ports[i], 'X ' + instrForm[-1])
                continue
            occ_ports[i] = list(tup)
            # Check if it's a ld including instr 
            p_flg = ''
            if self.en_par_ldst:
                # Check for ld
                # FIXME remove special load handling from here and place in machine model
                if (isinstance(instrForm[-2], MemAddr) or
                        (len(instrForm) > 4 and isinstance(instrForm[2], MemAddr))):
                    if par_ldst > 0:
                        par_ldst -= 1
                        p_flg = 'P '
                        for port in self.ld_ports:
                            occ_ports[i][port] = 0.0  # '(' + str(occ_ports[i][port]) + ')'
            # Write schedule line
            if len(p_flg) > 0:
                sched += self.format_port_occupation_line(occ_ports[i], p_flg + instrForm[-1])
                for port in self.ld_ports:
                    occ_ports[i][port] = 0
            else:
                sched += self.format_port_occupation_line(occ_ports[i], instrForm[-1])
            # Add throughput to total port binding
            port_bndgs = list(map(add, port_bndgs, occ_ports[i]))
        if machine_readable:
            list(map(self.append, occ_ports, self.instrList))
            return occ_ports, port_bndgs
        return sched, port_bndgs

    def schedule(self):
        """
        Schedule Instruction Form list and calculate port bindings.

        Returns
        -------
        (str, [int, ...])
            A tuple containing the graphic output of the schedule as string and
            the port bindings as list of ints.
        """
        wTP = False
        sched = self.get_head()
        # Initialize ports
        port_bndgs = [0] * self.ports
        # Check if there's a port occupation stored in the CSV, otherwise leave the
        # occ_port list item empty
        for i, instrForm in enumerate(self.instrList):
            try:
                search_string = instrForm[0] + '-' + self.get_operand_suffix(instrForm)
                entry = self.df.loc[lambda df, sStr=search_string: df.instr == sStr]
                tup = entry.ports.values[0]
                if len(tup) == 1 and tup[0][0] == -1:
                    raise IndexError()
            except IndexError:
                # Instruction form not in CSV
                if instrForm[0][:3] == 'nop':
                    sched += self.format_port_occupation_line(occ_ports[i], '* ' + instrForm[-1])
                else:
                    sched += self.format_port_occupation_line(occ_ports[i], 'X ' + instrForm[-1])
                continue
            if wTP:
                # Get the occurance of each port from the occupation list
                port_occurances = self.get_port_occurances(tup)
                # Get 'occurance groups'
                occurance_groups = self.get_occurance_groups(port_occurances)
                # Calculate port dependent throughput
                tp_ges = entry.TP.values[0] * len(occurance_groups[0])
                for occGroup in occurance_groups:
                    for port in occGroup:
                        occ_ports[i][port] = tp_ges / len(occGroup)
            else:
                variations = len(tup)
                t_all = self.flatten(tup)
                if entry.TP.values[0] == 0:
                    t_all = ()
                if variations == 1:
                    for j in tup[0]:
                        occ_ports[i][j] = entry.TP.values[0]
                else:
                    for j in range(0, self.ports):
                        occ_ports[i][j] = t_all.count(j) / variations
            # Write schedule line
            sched += self.format_port_occupation_line(occ_ports[i], instrForm[-1])
            # Add throughput to total port binding
            port_bndgs = list(map(add, port_bndgs, occ_ports[i]))
        return sched, port_bndgs

    def flatten(self, l):
        if len(l) == 0:
            return l
        if isinstance(l[0], type(l)):
            return self.flatten(l[0]) + self.flatten(l[1:])
        return l[:1] + self.flatten(l[1:])

    def append(self, l, e):
        if(isinstance(l, list)):
            l.append(e)
    
    def schedule_fcfs(self):
        """
        Schedule Instruction Form list for a single run with latencies.

        Returns
        -------
        (str, int)
            A tuple containing the graphic output as string and the total throughput time as int.
        """
        sched = self.get_head()
        total = 0
        # Initialize ports
        occ_ports = [0] * self.ports
        for instrForm in self.instrList:
            try:
                search_string = instrForm[0] + '-' + self.get_operand_suffix(instrForm)
                entry = self.df.loc[lambda df, sStr=search_string: df.instr == sStr]
                tup = entry.ports.values[0]
                if len(tup) == 1 and tup[0][0] == -1:
                    raise IndexError()
            except IndexError:
                # Instruction form not in CSV
                sched += self.format_port_occupation_line([0] * self.ports, '* ' + instrForm[-1])
                continue
            found = False
            while not found:
                for portOcc in tup:
                    # Test if chosen instruction form port occupation suits the current CPU port
                    # occupation
                    if self.test_ports_fcfs(occ_ports, portOcc):
                        # Current port occupation fits for chosen port occupation of instruction!
                        found = True
                        good = [entry.LT.values[0] if (j in portOcc) else 0 for j in
                                range(0, self.ports)]
                        sched += self.format_port_occupation_line(good, instrForm[-1])
                        # Add new occupation
                        occ_ports = [occ_ports[j] + good[j] for j in range(0, self.ports)]
                        break
                # Step
                occ_ports = [j - 1 if (j > 0) else 0 for j in occ_ports]
                if entry.LT.values[0] != 0:
                    total += 1
        total += max(occ_ports)
        return sched, total

    def get_occurance_groups(self, port_occurances):
        """
        Group ports in groups by the number of their occurrence and sorts groups by cardinality.

        Parameters
        ----------
        port_occurances : [int, ...]
            List with the length of ports containing the number of occurances
            of each port

        Returns
        -------
        [[int, ...], ...]
            List of lists with all occurance groups sorted by cardinality
            (smallest group first)
        """
        groups = [[] for x in range(len(set(port_occurances))-1)]
        for i, groupInd in enumerate(range(min(list(filter(lambda x: x > 0, port_occurances))),
                                           max(port_occurances) + 1)):
            for p, occurs in enumerate(port_occurances):
                if groupInd == occurs:
                    groups[i].append(p)
        # Sort groups by cardinality
        groups.sort(key=len)
        return groups

    def get_port_occurances(self, tups):
        """
        Return the number of each port occurrence for the possible port occupations.

        Parameters
        ----------
        tups : ((int, ...), ...)
            Tuple of tuples of possible port occupations

        Returns
        -------
        [int, ...]
            List in the length of the number of ports for the current architecture,
            containing the amount of occurances for each port
        """
        ports = [0] * self.ports
        for tup in tups:
            for elem in tup:
                ports[elem] += 1
        return ports

    def test_ports_fcfs(self, occ_ports, needed_ports):
        """
        Test if current configuration of ports is possible and returns boolean.

        Parameters
        ----------
        occ_ports : [int]
            Tuple to inspect for current port occupation
        needed_ports : (int)
            Tuple with needed port(s) for particular instruction form

        Returns
        -------
        bool
            True    if needed ports can get scheduled on current port occupation
            False   if not
        """
        for port in needed_ports:
            if occ_ports[port] != 0:
                return False
        return True

    def get_report_info(self):
        """
        Create Report information including all needed annotations.

        Returns
        -------
        str
            String containing the report information
        """
        analysis = 'Throughput Analysis Report\n' + ('-' * 26) + '\n'
        annotations = (
            'P - Load operation can be hidden behind a past or future store instruction\n'
            'X - No information for this instruction in data file\n'
            '* - Not bound to a port, therefore ignored\n\n')
        return analysis + annotations

    def get_head(self):
        """
        Create right heading for CPU architecture.

        Returns
        -------
        str
            String containing the header
        """
        port_names = self.get_port_naming()

        port_line = ''.join('|{:^6}'.format(pn) for pn in port_names) + '|\n'
        horiz_line = '-' * (len(port_line) - 1) + '\n'
        port_anno = ' ' * ((len(port_line) - 25) // 2) + 'Ports Pressure in cycles\n'

        return port_anno + port_line + horiz_line

    def format_port_occupation_line(self, occ_ports, instr_name):
        """
        Create line with port occupation for output.

        Parameters
        ----------
        occ_ports : (int, ...)
            Integer tuple containing needed ports
        instr_name : str
            Name of instruction form for output

        Returns
        -------
        str
            String for output containing port scheduling for instr_name
        """
        line = ''
        for cycles in occ_ports:
            if cycles == 0:
                line += '|' + ' ' * 6
            elif cycles >= 10:
                line += '|{:^6.1f}'.format(cycles)
            else:
                line += '|{:^6.2f}'.format(cycles)
        line += '| ' + instr_name + '\n'
        return line

    def get_port_naming(self):
        """
        Return list of port names

        :return: list of strings
        """
        return sorted([str(i) for i in range(self.ports)] + self.pipeline_ports)

    def get_port_binding(self, port_bndg):
        """
        Create port binding out of scheduling result.

        Parameters
        ----------
        port_bndg : [int, ...]
            Integer list containing port bindings

        Returns
        -------
        str
            String containing the port binding graphical output
        """
        col_widths = self.get_column_widths(port_bndg)
        header = 'Port Binding in Cycles Per Iteration:\n'
        horiz_line = '-' * 10 + '-' * (sum(col_widths) + len(col_widths)) + '\n'
        port_line = '|  Port  |'
        for i, port_name in enumerate(self.get_port_naming()):
            port_line += port_name.center(col_widths[i]) + '|'
        port_line += '\n'
        cyc_line = '| Cycles |'
        for i in range(len(port_bndg)):
            cyc_line += '{}|'.format(str(round(port_bndg[i], 2)).center(col_widths[i]))
        cyc_line += '\n'
        binding = header + horiz_line + port_line + horiz_line + cyc_line + horiz_line
        return binding

    def get_column_widths(self, port_bndg):
        return [max(len(str(round(x, 2))), len(name)) + 2
                for x, name in zip(port_bndg, self.get_port_naming())]

    def get_operand_suffix(self, instr_form):
        """
        Create operand suffix out of list of Parameters.

        Parameters
        ----------
        instr_form : [str, Parameter, ..., Parameter, str]
            Instruction Form data structure

        Returns
        -------
        str
            Operand suffix for searching in data file
        """
        op_ext = []
        operands = ''
        if len(instr_form) > 2:
            operands = '-'
        for i in range(1, len(instr_form) - 1):
            if isinstance(instr_form[i], Register) and instr_form[i].reg_type == 'GPR':
                optmp = 'r' + str(instr_form[i].size)
            elif isinstance(instr_form[i], MemAddr):
                optmp = 'mem'
            else:
                optmp = str(instr_form[i]).lower()
            op_ext.append(optmp)
        operands += '_'.join(op_ext)
        return operands


if __name__ == '__main__':
    print('Nothing to do.')
