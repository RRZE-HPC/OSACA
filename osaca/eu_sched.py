#!/usr/bin/python

import sys
import os
import math
import ast
from param import Register, MemAddr, Parameter
from operator import add
import pandas as pd


class Scheduler(object):

    arch_dict = {'SNB': 6, 'IVB': 6, 'HSW': 8, 'BDW': 8, 'SKL': 8}
    ports = None        # type: int
    instrList = None    # type: list<list<str,Param[,Param][,Param],str>>,
    # content of most inner list in instrList: instr, operand(s), instr form
    df = None           # type: DataFrame

    def __init__(self, arch, instructionList):
        arch = arch.upper()
        try:
            self.ports = self.arch_dict[arch]
        except KeyError:
            print('Architecture not supportet for EU scheduling.')
            sys.exit()
        self.instrList = instructionList
        currDir = os.path.realpath(__file__)[:-11]
        self.df = pd.read_csv(currDir + 'data/' + arch.lower() + '_data.csv', quotechar='"',
                              converters={'ports': ast.literal_eval})

    def schedule(self):
        """
        Schedules Instruction Form list and calculates port bindings.

        Returns
        -------
        (str, [int, ...])
            A tuple containing the graphic output of the schedule as string and
            the port bindings as list of ints.
        """
        sched = self.get_head()
        # Initialize ports
        occ_ports = [[0] * self.ports for x in range(len(self.instrList))]
        port_bndgs = [0] * self.ports
        # Check if there's a port occupation stored in the CSV, otherwise leave the
        # occ_port list item empty
        for i, instrForm in enumerate(self.instrList):
            try:
                search_string = instrForm[0] + '-' + self.get_operand_suffix(instrForm)
                entry = self.df.loc[lambda df, sStr=search_string: df.instr == sStr]
                tup = entry.ports.values[0]
                if(len(tup) == 1 and tup[0][0] == -1):
                    raise IndexError()
            except IndexError:
                # Instruction form not in CSV
                sched += self.get_line(occ_ports[i], '* ' + instrForm[-1])
                continue
            # Get the occurance of each port from the occupation list
            portOccurances = self.get_port_occurances(tup)
            # Get 'occurance groups'
            occuranceGroups = self.get_occurance_groups(portOccurances)
            # Calculate port dependent throughput
            TPGes = entry.TP.values[0] * len(occuranceGroups[0])
            for occGroup in occuranceGroups:
                for port in occGroup:
                    occ_ports[i][port] = TPGes/len(occGroup)
            # Write schedule line
            sched += self.get_line(occ_ports[i], instrForm[-1])
            # Add throughput to total port binding
            port_bndgs = list(map(add, port_bndgs, occ_ports[i]))
        return (sched, port_bndgs)

    def schedule_FCFS(self):
        """
        Schedules Instruction Form list for a single run with latencies.

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
                if(len(tup) == 1 and tup[0][0] == -1):
                    raise IndexError()
            except IndexError:
                # Instruction form not in CSV
                sched += self.get_line([0] * self.ports, '* ' + instrForm[-1])
                continue
            found = False
            while(not found):
                for portOcc in tup:
                    # Test if chosen instruction form port occupation suits the current CPU port
                    # occupation
                    if(self.test_ports_FCFS(occ_ports, portOcc)):
                        # Current port occupation fits for chosen port occupation of instruction!
                        found = True
                        good = [entry.LT.values[0] if (j in portOcc) else 0 for j in
                                range(0, self.ports)]
                        sched += self.get_line(good, instrForm[-1])
                        # Add new occupation
                        occ_ports = [occ_ports[j] + good[j] for j in range(0, self.ports)]
                        break
                # Step
                occ_ports = [j-1 if (j > 0) else 0 for j in occ_ports]
                if(entry.LT.values[0] != 0):
                    total += 1
        total += max(occ_ports)
        return (sched, total)

    def get_occurance_groups(self, portOccurances):
        """
        Groups ports in groups by the number of their occurance and sorts
        groups by cardinality

        Parameters
        ----------
        portOccurances : [int, ...]
            List with the length of ports containing the number of occurances
            of each port

        Returns
        -------
        [[int, ...], ...]
            List of lists with all occurance groups sorted by cardinality
            (smallest group first)
        """
        groups = [[] for x in range(len(set(portOccurances))-1)]
        for i, groupInd in enumerate(range(min(list(filter(lambda x: x > 0, portOccurances))),
                                           max(portOccurances) + 1)):
            for p, occurs in enumerate(portOccurances):
                if groupInd == occurs:
                    groups[i].append(p)
        # Sort groups by cardinality
        groups.sort(key=len)
        return groups

    def get_port_occurances(self, tups):
        """
        Returns the number of each port occurance for the possible port
        occupations

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

    def test_ports_FCFS(self, occ_ports, needed_ports):
        """
        Test if current configuration of ports is possible and returns boolean

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
            if(occ_ports[port] != 0):
                return False
        return True

    def get_report_info(self):
        """
        Creates Report information including all needed annotations.

        Returns
        -------
        str
            String containing the report information
        """
        analysis = 'Throughput Analysis Report\n' + ('-' * 26) + '\n'
        annotations = ('* - No information for this instruction in database\n'
                       '\n')
        return analysis + annotations

    def get_head(self):
        """
        Creates right heading for CPU architecture.

        Returns
        -------
        str
            String containing the header
        """
        horizLine = '-' * 7 * self.ports + '-\n'
        portAnno = (' ' * (math.floor((len(horizLine) - 24) / 2)) + 'Ports Pressure in cycles'
                    + ' ' * (math.ceil((len(horizLine) - 24) / 2)) + '\n')
        portLine = ''
        for i in range(0, self.ports):
            portLine += '|  {}   '.format(i)
        portLine += '|\n'
        head = portAnno + portLine + horizLine
        return head

    def get_line(self, occ_ports, instrName):
        """
        Create line with port occupation for output.

        Parameters
        ----------
        occ_ports : (int, ...)
            Integer tuple containing needed ports
        instrName : str
            Name of instruction form for output

        Returns
        -------
        str
            String for output containing port scheduling for instrName
        """
        line = ''
        for i in occ_ports:
            cycles = '    ' if (i == 0) else '%.2f' % float(i)
            line += '| ' + cycles + ' '
        line += '| ' + instrName + '\n'
        return line

    def get_port_binding(self, port_bndg):
        """
        Creates port binding out of scheduling result.

        Parameters
        ----------
        port_bndg : [int, ...]
            Integer list containing port bindings

        Returns
        -------
        str
            String containing the port binding graphical output
        """
        header = 'Port Binding in Cycles Per Iteration:\n'
        horizLine = '-' * 10 + '-' * 6 * self.ports + '\n'
        portLine = '|  Port  |'
        for i in range(0, self.ports):
            portLine += '  {}  |'.format(i)
        portLine += '\n'
        cycLine = '| Cycles |'
        for i in range(len(port_bndg)):
            cycLine += ' {} |'.format(round(port_bndg[i], 2))
        cycLine += '\n'
        binding = header + horizLine + portLine + horizLine + cycLine + horizLine
        return binding

    def get_operand_suffix(self, instrForm):
        """
        Creates operand suffix out of list of Parameters.

        Parameters
        ----------
        instrForm : [str, Parameter, ..., Parameter, str]
            Instruction Form data structure

        Returns
        -------
        str
            Operand suffix for searching in database
        """
        opExt = []
        for i in range(1, len(instrForm)-1):
            optmp = ''
            if(isinstance(instrForm[i], Register) and instrForm[i].reg_type == 'GPR'):
                optmp = 'r' + str(instrForm[i].size)
            elif(isinstance(instrForm[i], MemAddr)):
                optmp = 'mem'
            else:
                optmp = str(instrForm[i]).lower()
            opExt.append(optmp)
        operands = '_'.join(opExt)
        return operands


if __name__ == '__main__':
    # data = [
    # ['lea',Register('RAX'),MemAddr('%edx,(%rax,%rax,1)'),'lea    0x1(%rax,%rax,1),%edx'],
    # ['vcvtsi2ss',Register('XMM0'),Register('XMM0'),Register('RAX'),'vcvtsi2ss %edx,%xmm2,%xmm2'],
    # ['vmulss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vmulss %xmm2,%xmm0,%xmm3'],
    # ['lea',Register('RAX'),MemAddr('%edx,(%rax,%rax,1)'),'lea    0x2(%rax,%rax,1),%ecx'],
    # ['vaddss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vaddss %xmm3,%xmm1,%xmm4'],
    # ['vxorps',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vxorps %xmm1, %xmm1,%xmm1'],
    # ['vcvtsi2ss',Register('XMM0'),Register('XMM0'),Register('RAX'),'vcvtsi2ss %ecx,%xmm1,%xmm1'],
    # ['vmulss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vmulss %xmm1,%xmm0,%xmm5'],
    # ['vmovss',MemAddr('%edx,(%rax,%rax,1)'),Register('XMM0'),'vmovss %xmm4,0x4(%rsp,%rax,8)'],
    # ['vaddss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vaddss %xmm5,%xmm4,%xmm1'],
    # ['vmovss',MemAddr('%edx,(%rax,%rax,1)'),Register('XMM0'),'vmovss %xmm1,0x8(%rsp,%rax,8)'],
    # ['inc',Register('RAX'),'inc    %rax'],
    # ['cmp',Register('RAX'),Parameter('IMD'),'cmp    $0x1f3,%rax'],
    # ['jb',Parameter('LBL'),'jb             400bc2 <main+0x62>']
    # ]

    # sched = Scheduler('ivb', data)
    # output,binding = sched.schedule()
    # print(sched.get_port_binding(binding))
    # print(sched.get_report_info(),end='')
    # print(output)
    # print('Block Throughput: {}'.format(round(max(binding),2)))
