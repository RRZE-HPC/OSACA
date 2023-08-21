#!/usr/bin/env python3

from osaca.parser.directive import DirectiveOperand

class InstructionForm:
    # Identifiers for operand types
    COMMENT_ID = "comment"
    DIRECTIVE_ID = "directive"
    IMMEDIATE_ID = "immediate"
    LABEL_ID = "label"
    IDENTIFIER_ID = "identifier"
    MEMORY_ID = "memory"
    REGISTER_ID = "register"
    SEGMENT_EXT_ID = "segment_extension"
    INSTRUCTION_ID = "instruction"
    OPERANDS_ID = "operands"

    def __init__(self, INSTRUCTION_ID = None, OPERANDS_ID = [], DIRECTIVE_ID = None
    , COMMENT_ID = None, LABEL_ID = None, LINE = None, LINE_NUMBER = None
    , SEMANTIC_OPERANDS = None):
        self._INSTRUCTION_ID = INSTRUCTION_ID
        self._OPERANDS_ID = OPERANDS_ID
        self._DIRECTIVE_ID = DIRECTIVE_ID
        self._COMMENT_ID = COMMENT_ID
        self._LABEL_ID = LABEL_ID
        self._LINE = LINE
        self._LINE_NUMBER = LINE_NUMBER

        self._SEMANTIC_OPERANDS = SEMANTIC_OPERANDS
        self._UOPS = None
        #self.semantic_operands = {"source": [], "destination": [], "src_dst": []}
        self._LATENCY = None
        self._THROUGHPUT = None
        self._LATENCY_CP = []
        self._LATENCY_LCD = []
        self._LATENCY_WO_LOAD = None
        self._PORT_PRESSURE = []
        self._PORT_UOPS = []
        self._FLAGS = []

    @property
    def semantic_operands(self):
        return self._SEMANTIC_OPERANDS

    @property
    def instruction(self):
        return self._INSTRUCTION_ID
    
    @property
    def label(self):
        return self._LABEL_ID

    @property
    def comment(self):
        return self._COMMENT_ID

    @property
    def directive(self):
        return self._DIRECTIVE_ID

    @property
    def line_number(self):
        return self._LINE_NUMBER
    
    @property
    def line(self):
        return self._LINE
    
    @property
    def operands(self):
        return self._OPERANDS_ID

    @property
    def port_pressure(self):
        return self._PORT_PRESSURE
    
    @property
    def port_uops(self):
        return self._PORT_UOPS
    
    @property
    def flags(self):
        return self._FLAGS

    @semantic_operands.setter
    def semantic_operands(self, semantic_operands):
        self._SEMANTIC_OPERANDS = semantic_operands

    @directive.setter
    def directive(self, directive):
        self._DIRECTIVE_ID = directive

    @line_number.setter
    def line_number(self, line_number):
        self._LINE_NUMBER = line_number
    
    @line.setter
    def line(self, line):
        self._LINE = line
    
    @operands.setter
    def operands(self, operands):
        self._OPERANDS_ID = operands

    @instruction.setter
    def instruction(self, instruction):
        self._INSTRUCTION_ID = instruction
    
    @label.setter
    def label(self, label):
        self._LABEL_ID = label

    @comment.setter
    def comment(self, comment):
        self._COMMENT_ID =comment

    @port_pressure.setter
    def port_pressure(self, port_pressure):
        self._PORT_PRESSURE = port_pressure
    
    @port_uops.setter
    def port_uops(self, port_uops):
        self._PORT_UOPS = port_uops

    @flags.setter
    def flags(self, flags):
        self._FLAGS = flags

    def __repr__(self):
        return f"InstructionForm(INSTRUCTION_ID={self._INSTRUCTION_ID}, OPERANDS_ID={self._OPERANDS_ID}, DIRECTIVE_ID={self._DIRECTIVE_ID}, COMMENT_ID={self._COMMENT_ID}, LABEL_ID={self._LABEL_ID}, LINE={self._LINE}, LINE_NUMBER={self._LINE_NUMBER}, SEMANTIC_OPERANDS={self._SEMANTIC_OPERANDS})"

    def __str__(self):
        return f"Instruction: {self._INSTRUCTION_ID}\nOperands: {self._OPERANDS_ID}\nDirective: {self._DIRECTIVE_ID}\nComment: {self._COMMENT_ID}\nLabel: {self._LABEL_ID}\nLine: {self._LINE}\nLine Number: {self._LINE_NUMBER}\nSemantic Operands: {self._SEMANTIC_OPERANDS}"

    def __eq__(self, other):
        if isinstance(other, InstructionForm):
            return (
                self._INSTRUCTION_ID == other._INSTRUCTION_ID and
                self._OPERANDS_ID == other._OPERANDS_ID and
                self._DIRECTIVE_ID == other._DIRECTIVE_ID and
                self._COMMENT_ID == other._COMMENT_ID and
                self._LABEL_ID == other._LABEL_ID and
                self._LINE == other._LINE and
                self._LINE_NUMBER == other._LINE_NUMBER and
                self._SEMANTIC_OPERANDS == other._SEMANTIC_OPERANDS
            )
        return False
        