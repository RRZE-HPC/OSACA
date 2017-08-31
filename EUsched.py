#!/apps/python/3.5-anaconda/bin/python

import sys
import os
import math
import ast
from Params import *
import pandas as pd

class Scheduler(object):
    arch_dict = {'SNB':6, 'IVB':6, 'HSW':8, 'BDW':8, 'SKL':8}
    ports = None        #type: int
    instrList = None    #type: list<list<str,Param[,Param][,Param],str>>
                        #               instr, operand(s), instr form
    df = None           #type: DataFrame


    def __init__(self, arch, instructionList):
        arch = arch.upper()
        try:
            self.ports = self.arch_dict[arch]
        except KeyError:
            print('Architecture not supportet for EU scheduling.')
            sys.exit()
        self.instrList = instructionList
        currDir = os.path.realpath(__file__)[:-10]
        self.df = pd.read_csv(currDir+'data/'+arch.lower()+'_data.csv', quotechar='"', converters={'ports':ast.literal_eval})


    def schedule_FCFS(self):
        '''
        Schedules Instruction Form list via First Come First Serve algorithm.

        Returns 
        -------
        (str, int)
            A tuple containing the graphic output as string and the total throughput time as int.
        '''
        sched = ''
        total = 0
# Initialize ports
        occ_ports = [0]*self.ports
        for i,instrForm in enumerate(self.instrList):
            try:
                searchString = instrForm[0]+'-'+self.get_operand_suffix(instrForm)
                entry = self.df.loc[lambda df: df.instr == searchString,'LT':'ports']
                tup = entry.ports.values[0]
                if(len(tup) == 1 and tup[0][0] == -1):
                    raise IndexError()
            except IndexError:
# Instruction form not in CSV
                sched += self.get_line([0]*self.ports,'* '+instrForm[-1])
                continue
            found = False
            while(not found):
                for portOcc in tup:
# Test if chosen instruction form port occupation suits the current CPU port occupation
                    if(self.test_ports_FCFS(occ_ports, portOcc)):
# Current port occupation fits for chosen port occupation of the instruction!
                        found = True
                        good = [entry.LT.values[0] if (j in portOcc) else 0 for j in range(0,self.ports)]
                        sched += self.get_line(good, instrForm[-1])
# Add new occupation
                        occ_ports = [occ_ports[j]+good[j] for j in range(0, self.ports)]
                        break
# Step
                occ_ports = [j-1 if (j > 0) else 0 for j in occ_ports]                
                if(entry.LT.values[0] != 0):
                    total += 1
        total += max(occ_ports)
        return (sched, total)

    def test_ports_FCFS(self, occ_ports, needed_ports):
        '''
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
        '''
        for port in needed_ports:
            if(occ_ports[port] != 0):
                return False
        return True

    def schedule_Tomasulo(self):
        '''
        Not implement yet.  Schedules Instruction Form list via Tomasulo algorithm.
        '''
        print('Scheduling with Tomasulo algorithm...')
        return ''

    def get_head(self):
        '''
        Creates right heading for CPU architecture.

        Returns
        -------
        str
            String containing the header
        '''
        analysis = 'Throughput Analysis Report\n'+('-'*26)+'\n'
        annotations = ( '* - No information for this instruction in database\n'
                        '\n')
        horizLine = '-'*6*self.ports+'-\n'
        portAnno = ' '*(math.floor((len(horizLine)-24)/2))+'Ports Pressure in cycles'+' '*(math.ceil((len(horizLine)-24)/2))+'\n'
        portLine = ''
        for i in range(0,self.ports):
            portLine += '|  {}  '.format(i)
        portLine += '|\n'
        head = analysis+annotations+portAnno+portLine + horizLine
        return head

    def get_line(self, occ_ports, instrName):
        '''
        Create line with port occupation for output.

        Parameters
        ----------
        occ_ports : (int)
            Integer tuple containing needed ports
        instrName : str
            Name of instruction form for output

        Returns
        -------
        str
            String for output containing port scheduling for instrName
        '''
        line = ''
        for i in occ_ports:
            cycles = '   ' if (i == 0) else float(i)
            line += '| '+str(cycles)+' '
        line += '| '+instrName+'\n'
        return line


    def get_operand_suffix(self, instrForm):
        '''
        Creates operand suffix out of list of Parameters.

        Parameters
        ----------
        instrForm : [str, Parameter, ..., Parameter, str]
            Instruction Form data structure

        Returns
        -------
        str
            Operand suffix for searching in database
        '''
        extension = ''
        opExt = []
        for i in range(1, len(instrForm)-1):
            optmp = ''
            if(isinstance(instrForm[i], Register) and instrForm[i].reg_type == 'GPR'):
                optmp = 'r'+str(instrForm[i].size)
            elif(isinstance(instrForm[i], MemAddr)):
                optmp = 'mem'
            else:
                optmp = instrForm[i].print().lower()
            opExt.append(optmp)
        operands = '_'.join(opExt)
        return operands


if __name__ == '__main__':
    data = [
    ['lea',Register('RAX'),MemAddr('%edx,(%rax,%rax,1)'),'lea    0x1(%rax,%rax,1),%edx'],
    ['vcvtsi2ss',Register('XMM0'),Register('XMM0'),Register('RAX'),'vcvtsi2ss %edx,%xmm2,%xmm2'],
    ['vmulss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vmulss %xmm2,%xmm0,     %xmm3'],
    ['lea',Register('RAX'),MemAddr('%edx,(%rax,%rax,1)'),'lea    0x2(%rax,%rax,1),%ecx'],
    ['vaddss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vaddss %xmm3,%xmm1,%xmm4'],
    ['vxorps',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vxorps %xmm1, %xmm1,%xmm1'],
    ['vcvtsi2ss',Register('XMM0'),Register('XMM0'),Register('RAX'),'vcvtsi2ss %ecx,%xmm1, %xmm1'],
    ['vmulss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vmulss %xmm1,%xmm0,%xmm5'],
    ['vmovss',MemAddr('%edx,(%rax,%rax,1)'),Register('XMM0'),'vmovss %xmm4,0x4(%rsp,%rax,8)'],
    ['vaddss',Register('XMM0'),Register('XMM0'),Register('XMM0'),'vaddss %xmm5,%xmm4,%xmm1'],
    ['vmovss',MemAddr('%edx,(%rax,%rax,1)'),Register('XMM0'),'vmovss %xmm1,0x8(%rsp,%rax,8)'],
    ['inc',Register('RAX'),'inc    %rax'],
    ['cmp',Register('RAX'),Parameter('IMD'),'cmp    $0x1f3,%rax'],
    ['jb',Parameter('LBL'),'jb             400bc2 <main+0x62>']
    ]

    sched = Scheduler('skl', data)
    print(sched.get_head(),end='')
    output,total = sched.schedule_FCFS()
    print(output)
    print('Total number of estimated throughput: '+str(total))
