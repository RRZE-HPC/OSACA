#!/usr/bin/env python3
import re


class Parameter(object):
    type_list = ['REG', 'MEM', 'IMD', 'LBL', 'NONE']

    def __init__(self, ptype):
        self.ptype = ptype.upper()
        if self.ptype not in self.type_list:
            raise NameError('Type not supported: '+ptype)

    def __str__(self):
        """Return string representation."""
        if self.ptype == 'NONE':
            return ''
        else:
            return self.ptype


class MemAddr(Parameter):
    segment_regs = ['CS', 'DS', 'SS', 'ES', 'FS', 'GS']
    scales = [1, 2, 4, 8]

    def __init__(self, name):
        super().__init__("MEM")
        name = name.strip(', \t')
        self.offset = None
        self.base = None
        self.index = None
        self.scale = None
        
        m = re.match(r'((?P<offset_hex>[x0-9a-fA-F]*)|(?P<offset_dec>\-?[0-9]*))'
                     r'\((?P<base>[^,\)]+)(?:,\s*(?P<index>[^,\)]+)(?:,\s*'
                     r'(?P<scale>[^,\)]+))?)?\)', name)

        if not m:
            raise ValueError('Type not supported: {!r}'.format(name))

        self.offset = m.group('offset_dec') or m.group('offset_hex') or None
        self.base = m.group('base') or None
        self.index = m.group('index') or None
        self.scale = m.group('scale') or None


    def __str__(self):
        """returns string representation"""
        mem_format = 'MEM('
        if self.offset:
            mem_format += 'offset'
        if self.base and not self.index:
            mem_format += '(base)'
        elif self.base and self.index and self.scale:
            mem_format += '(base, index, scale)'
        mem_format += ')'
        return mem_format


class Register(Parameter):
    sizes = {
        # General Purpose Registers
        'AH': (8, 'GPR'), 'AL': (8, 'GPR'), 'BH': (8, 'GPR'), 'BL': (8, 'GPR'), 'CH': (8, 'GPR'),
        'CL': (8, 'GPR'), 'DH': (8, 'GPR'), 'DL': (8, 'GPR'), 'BPL': (8, 'GPR'), 'SIL': (8, 'GPR'),
        'DIL': (8, 'GPR'), 'SPL': (8, 'GPR'), 'R8L': (8, 'GPR'), 'R9L': (8, 'GPR'),
        'R10L': (8, 'GPR'), 'R11L': (8, 'GPR'), 'R12L': (8, 'GPR'), 'R13L': (8, 'GPR'),
        'R14L': (8, 'GPR'), 'R15L': (8, 'GPR'), 'R8B': (8, 'GPR'), 'R9B': (8, 'GPR'),
        'R10B': (8, 'GPR'), 'R11B': (8, 'GPR'), 'R12B': (8, 'GPR'), 'R13B': (8, 'GPR'),
        'R14B': (8, 'GPR'), 'R15B': (8, 'GPR'), 'AX': (16, 'GPR'), 'BC': (16, 'GPR'),
        'CX': (16, 'GPR'), 'DX': (16, 'GPR'), 'BP': (16, 'GPR'), 'SI': (16, 'GPR'),
        'DI': (16, 'GPR'), 'SP': (16, 'GPR'), 'R8W': (16, 'GPR'), 'R9W': (16, 'GPR'),
        'R10W': (16, 'GPR'), 'R11W': (16, 'GPR'), 'R12W': (16, 'GPR'), 'R13W': (16, 'GPR'),
        'R14W': (16, 'GPR'), 'R15W': (16, 'GPR'), 'EAX': (32, 'GPR'), 'EBX': (32, 'GPR'),
        'ECX': (32, 'GPR'), 'EDX': (32, 'GPR'), 'EBP': (32, 'GPR'), 'ESI': (32, 'GPR'),
        'EDI': (32, 'GPR'), 'ESP': (32, 'GPR'), 'R8D': (32, 'GPR'), 'R9D': (32, 'GPR'),
        'R10D': (32, 'GPR'), 'R11D': (32, 'GPR'), 'R12D': (32, 'GPR'), 'R13D': (32, 'GPR'),
        'R14D': (32, 'GPR'), 'R15D': (32, 'GPR'), 'RAX': (64, 'GPR'), 'RBX': (64, 'GPR'),
        'RCX': (64, 'GPR'), 'RDX': (64, 'GPR'), 'RBP': (64, 'GPR'), 'RSI': (64, 'GPR'),
        'RDI': (64, 'GPR'), 'RSP': (64, 'GPR'), 'R8': (64, 'GPR'), 'R9': (64, 'GPR'),
        'R10': (64, 'GPR'), 'R11': (64, 'GPR'), 'R12': (64, 'GPR'), 'R13': (64, 'GPR'),
        'R14': (64, 'GPR'), 'R15': (64, 'GPR'), 'CS': (16, 'GPR'), 'DS': (16, 'GPR'),
        'SS': (16, 'GPR'), 'ES': (16, 'GPR'), 'FS': (16, 'GPR'), 'GS': (16, 'GPR'),
        'EFLAGS': (32, 'GPR'), 'RFLAGS': (64, 'GPR'), 'EIP': (32, 'GPR'), 'RIP': (64, 'GPR'),
        # FPU Registers
        'ST0': (80, 'FPU'), 'ST1': (80, 'FPU'), 'ST2': (80, 'FPU'), 'ST3': (80, 'FPU'),
        'ST4': (80, 'FPU'), 'ST5': (80, 'FPU'), 'ST6': (80, 'FPU'), 'ST7': (80, 'FPU'),
        # MMX Registers
        'MM0': (64, 'MMX'), 'MM1': (64, 'MMX'), 'MM2': (64, 'MMX'), 'MM3': (64, 'MMX'),
        'MM4': (64, 'MMX'), 'MM5': (64, 'MMX'), 'MM6': (64, 'MMX'), 'MM7': (64, 'MMX'),
        # XMM Registers
        'XMM0': (128, 'XMM'), 'XMM1': (128, 'XMM'), 'XMM2': (128, 'XMM'), 'XMM3': (128, 'XMM'),
        'XMM4': (128, 'XMM'), 'XMM5': (128, 'XMM'), 'XMM6': (128, 'XMM'), 'XMM7': (128, 'XMM'),
        'XMM8': (128, 'XMM'), 'XMM9': (128, 'XMM'), 'XMM10': (128, 'XMM'), 'XMM11': (128, 'XMM'),
        'XMM12': (128, 'XMM'), 'XMM13': (128, 'XMM'), 'XMM14': (128, 'XMM'), 'XMM15': (128, 'XMM'),
        'XMM16': (128, 'XMM'), 'XMM17': (128, 'XMM'), 'XMM18': (128, 'XMM'), 'XMM19': (128, 'XMM'),
        'XMM20': (128, 'XMM'), 'XMM21': (128, 'XMM'), 'XMM22': (128, 'XMM'), 'XMM23': (128, 'XMM'),
        'XMM24': (128, 'XMM'), 'XMM25': (128, 'XMM'), 'XMM26': (128, 'XMM'), 'XMM27': (128, 'XMM'),
        'XMM28': (128, 'XMM'), 'XMM29': (128, 'XMM'), 'XMM30': (128, 'XMM'), 'XMM31': (128, 'XMM'),
        # YMM Registers
        'YMM0': (256, 'YMM'), 'YMM1': (256, 'YMM'), 'YMM2': (256, 'YMM'), 'YMM3': (256, 'YMM'),
        'YMM4': (256, 'YMM'), 'YMM5': (256, 'YMM'), 'YMM6': (256, 'YMM'), 'YMM7': (256, 'YMM'),
        'YMM8': (256, 'YMM'), 'YMM9': (256, 'YMM'), 'YMM10': (256, 'YMM'), 'YMM11': (256, 'YMM'),
        'YMM12': (256, 'YMM'), 'YMM13': (256, 'YMM'), 'YMM14': (256, 'YMM'), 'YMM15': (256, 'YMM'),
        'YMM16': (256, 'YMM'), 'YMM17': (256, 'YMM'), 'YMM18': (256, 'YMM'), 'YMM19': (256, 'YMM'),
        'YMM20': (256, 'YMM'), 'YMM21': (256, 'YMM'), 'YMM22': (256, 'YMM'), 'YMM23': (256, 'YMM'),
        'YMM24': (256, 'YMM'), 'YMM25': (256, 'YMM'), 'YMM26': (256, 'YMM'), 'YMM27': (256, 'YMM'),
        'YMM28': (256, 'YMM'), 'YMM29': (256, 'YMM'), 'YMM30': (256, 'YMM'), 'YMM31': (256, 'YMM'),
        # ZMM Registers
        'ZMM0': (512, 'ZMM'), 'ZMM1': (512, 'ZMM'), 'ZMM2': (512, 'ZMM'), 'ZMM3': (512, 'ZMM'),
        'ZMM4': (512, 'ZMM'), 'ZMM5': (512, 'ZMM'), 'ZMM6': (512, 'ZMM'), 'ZMM7': (512, 'ZMM'),
        'ZMM8': (512, 'ZMM'), 'ZMM9': (512, 'ZMM'), 'ZMM10': (512, 'ZMM'), 'ZMM11': (512, 'ZMM'),
        'ZMM12': (512, 'ZMM'), 'ZMM13': (512, 'ZMM'), 'ZMM14': (512, 'ZMM'), 'ZMM15': (512, 'ZMM'),
        'ZMM16': (512, 'ZMM'), 'ZMM17': (512, 'ZMM'), 'ZMM18': (512, 'ZMM'), 'ZMM19': (512, 'ZMM'),
        'ZMM20': (512, 'ZMM'), 'ZMM21': (512, 'ZMM'), 'ZMM22': (512, 'ZMM'), 'ZMM23': (512, 'ZMM'),
        'ZMM24': (512, 'ZMM'), 'ZMM25': (512, 'ZMM'), 'ZMM26': (512, 'ZMM'), 'ZMM27': (512, 'ZMM'),
        'ZMM28': (512, 'ZMM'), 'ZMM29': (512, 'ZMM'), 'ZMM30': (512, 'ZMM'), 'ZMM31': (512, 'ZMM'),
        # Opmask Register
        'K0': (64, 'K'), 'K1': (64, 'K'), 'K2': (64, 'K'), 'K3': (64, 'K'), 'K4': (64, 'K'),
        'K5': (64, 'K'), 'K6': (64, 'K'), 'K7': (64, 'K'),
        # Bounds Registers
        'BND0': (128, 'BND'), 'BND1': (128, 'BND'), 'BND2': (128, 'BND'), 'BND3': (128, 'BND'),
        # Registers in gerneral
        'R16': (16, 'GPR'), 'R32': (32, 'GPR'), 'R64': (64, 'GPR'), 'FPU': (80, 'FPU'),
        'MMX': (64, 'MMX'), 'XMM': (128, 'XMM'), 'YMM': (256, 'YMM'), 'ZMM': (512, 'ZMM'),
        'K': (64, 'K'), 'BND': (128, 'BND')
    }

    def __init__(self, name, mask=False):
        super().__init__("REG")
        self.name = name.upper()
        self.mask = mask
        if self.name in self.sizes:
            self.size = self.sizes[self.name][0]
            self.reg_type = self.sizes[self.name][1]
        else:
            raise NameError('Register name not in dictionary: {}'.format(self.name))

    def __str__(self):
        """Return string representation."""
        opmask = ''
        if self.mask:
            opmask = '{opmask}'
        return self.reg_type + opmask
