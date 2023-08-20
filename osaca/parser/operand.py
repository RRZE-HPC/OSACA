#!/usr/bin/env python3

class Operand:
    def __init__(self, MEMORY_ID = None, IMMEDIATE_ID = None, DIRECTIVE_ID = None, LABEL_ID = None
    , COMMENT_ID = None, REGISTER_ID = None, IDENTIFIER_ID = None, CONDITION_ID = None):
        self._MEMORY_ID = MEMORY_ID
        self._IMMEDIATE_ID = IMMEDIATE_ID
        self._DIRECTIVE_ID = DIRECTIVE_ID
        self._LABEL_ID = LABEL_ID
        self._COMMENT_ID = COMMENT_ID
        self._REGISTER_ID = REGISTER_ID
        self._IDENTIFIER_ID = IDENTIFIER_ID
        self._CONDITION_ID = CONDITION_ID

    @property
    def memory(self):
        return self._MEMORY_ID

    @property
    def condition(self):
        return self._CONDITION_ID
    
    @property
    def immediate(self):
        return self._IMMEDIATE_ID
    
    @property
    def directive(self):
        return self._DIRECTIVE_ID    

    @property
    def label(self):
        return self._LABEL_ID
    
    @property
    def comment(self):
        return self._COMMENT_ID

    @property
    def register(self):
        return self._REGISTER_ID

    @property
    def identifier(self):
        return self._IDENTIFIER_ID

    def copyFrom(self, operand_dict):
        #self._COMMENT_ID = operand_dict["comment"] if "comment" in operand_dict else None
        for key, value in operand_dict.items():
            setattr(self, key, value)

    @memory.setter
    def memory(self, memory):
        self._MEMORY_ID = memory
    
    @immediate.setter
    def immediate(self, immediate):
        self._IMMEDIATE_ID = immediate
    
    @directive.setter
    def directive(self, directive):
        self._DIRECTIVE_ID = directive    

    @label.setter
    def label(self, label):
        self._LABEL_ID = label

    @comment.setter
    def comment(self, comment):
        self._COMMENT_ID = comment

    @register.setter
    def register(self, register):
        self._REGISTER_ID = register

    @identifier.setter
    def identifier(self, identifier):
        self._IDENTIFIER_ID = identifier

    @condition.setter
    def condition(self, condition):
        self._CONDITION_ID = condition
    
    def __repr__(self):
        return f"Operand(MEMORY_ID={self._MEMORY_ID}, IMMEDIATE_ID={self._IMMEDIATE_ID}, DIRECTIVE_ID={self._DIRECTIVE_ID}, LABEL_ID={self._LABEL_ID}, COMMENT_ID={self._COMMENT_ID}), REGISTER_ID={self._REGISTER_ID}, IDENTIFIER_ID={self._IDENTIFIER_ID})"

    def __str__(self):
        return f"Memory: {self._MEMORY_ID}\nImmediate: {self._IMMEDIATE_ID}\nDirective: {self._DIRECTIVE_ID}\nLabel: {self._LABEL_ID}\nComment: {self._COMMENT_ID}\nRegister: {self._REGISTER_ID}\nIdentifier: {self._IDENTIFIER_ID}"