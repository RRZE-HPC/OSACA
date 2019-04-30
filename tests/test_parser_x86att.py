#!/usr/bin/env python3
"""
Unit tests for x86 AT&T assembly parser
"""

import unittest

from pyparsing import ParseException

from osaca.parser import ParserX86ATT


class TestParserX86ATT(unittest.TestCase):
    def setUp(self):
        self.parser = ParserX86ATT()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(get_comment(self.parser, '# some comments'), 'some comments')
        self.assertEqual(get_comment(self.parser, '\t\t#AA BB CC \t end \t'), 'AA BB CC end')
        self.assertEqual(
            get_comment(self.parser, '\t## comment ## comment'), '# comment ## comment'
        )

    def test_label_parser(self):
        self.assertEqual(get_label(self.parser, 'main:')['name'], 'main')
        self.assertEqual(get_label(self.parser, '..B1.10:')['name'], '.B1.10')
        self.assertEqual(get_label(self.parser, '.2.3_2_pack.3:')['name'], '.2.3_2_pack.3')
        self.assertEqual(get_label(self.parser, '.L1:\t\t\t#label1')['name'], '.L1')
        self.assertEqual(get_label(self.parser, '.L1:\t\t\t#label1')['comment'], 'label1')
        with self.assertRaises(ParseException):
            get_label(self.parser, '\t.cfi_startproc')

    def test_directive_parser(self):
        self.assertEqual(get_directive(self.parser, '\t.text')['name'], 'text')
        self.assertEqual(len(get_directive(self.parser, '\t.text')['parameters']), 0)
        self.assertEqual(get_directive(self.parser, '\t.align\t16,0x90')['name'], 'align')
        self.assertEqual(len(get_directive(self.parser, '\t.align\t16,0x90')['parameters']), 2)
        self.assertEqual(get_directive('\t.align\t16,0x90')['parameters'][1], '0x90')
        self.assertEqual(
            get_directive(self.parser, '        .byte 100,103,144       #IACA START')['name'],
            'byte',
        )
        self.assertEqual(
            get_directive(self.parser, '        .byte 100,103,144       #IACA START')[
                'parameters'
            ][2],
            '144',
        )
        self.assertEqual(
            get_directive(self.parser, '        .byte 100,103,144       #IACA START')['comment'],
            'IACA START',
        )

    def test_parse_instruction(self):
        instr1 = '\t\tvcvtsi2ss %edx, %xmm2, %xmm2\t\t\t#12.27'
        instr2 = 'jb        ..B1.4 \t'
        instr3 = '        movl $222,%ebx          #IACA END'
        instr4 = 'vmovss    %xmm4, -4(%rsp,%rax,8) #12.9'

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)

        self.assertEqual(parsed_1['instruction'], 'vcvtsi2ss')
        self.assertEqual(parsed_1['operands']['destination']['register']['name'], 'xmm2')
        self.assertEqual(parsed_1['operands']['sources'][0]['register']['name'], 'edx')
        self.assertEqual(parsed_1['comment'], '12.27')

        self.assertEqual(parsed_2['instruction'], 'jb')
        self.assertEqual(parsed_2['operands']['destination'], '..B1.4')
        self.assertEqual(len(parsed_2['operands']['sources']), 0)
        self.assertIsNone(parsed_2['comment'])

        self.assertEqual(parsed_3['instruction'], 'movl')
        self.assertEqual(parsed_3['operands']['destination']['register']['name'], 'ebx')
        self.assertEqual(parsed_3['operands']['sources'][0]['immediate']['value'], '222')
        self.assertEqual(parsed_3['comment'], 'IACA END')

        self.assertEqual(parsed_4['instruction'], 'vmovss')
        self.assertEqual(parsed_4['operands']['destination']['memory']['offset'], '-4')
        self.assertEqual(parsed_4['operands']['destination']['memory']['base'], 'rsp')
        self.assertEqual(parsed_4['operands']['destination']['memory']['index'], 'rax')
        self.assertEqual(parsed_4['operands']['destination']['memory']['scale'], '8')
        self.assertEqual(parsed_4['operands']['sources'][0]['register']['name'], 'xmm4')
        self.assertEqual(parsed_4['comment'], '12.9')

    def test_parse_line(self):
        line_comment = '# -- Begin  main'
        line_label = '..B1.7:                         # Preds ..B1.6'
        line_directive = '\t\t.quad   .2.3_2__kmpc_loc_pack.2 #qed'
        # line_instruction = '\t\tlea       2(%rax,%rax), %ecx #12.9'

        instruction_form_1 = {
            'instruction': None,
            'operands': None,
            'directive': None,
            'comment': '-- Begin main',
            'label': None,
            'line_number': 1,
        }
        instruction_form_2 = {
            'instruction': None,
            'operands': None,
            'directive': None,
            'comment': None,
            'label': '..B1.7',
            'line_number': 2,
        }
        instruction_form_3 = {
            'instruction': None,
            'operands': None,
            'directive': {'name': 'quad', 'parameters': ['.2.3_2__kmpc_loc_pack.2']},
            'comment': 'qed',
            'label': None,
            'line_number': 3,
        }
        # TODO
        # instruction_form_4 = {
        #    'instruction': 'lea',
        #    'operands': {'sources': {'memory': {'offset': '2', 'base': {'name': rax}, ''}}},
        #    'directive': None,
        #    'comment': '-- Begin main',
        #    'label': None,
        #    'line_number': 1,
        # }

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        # TODO parsed_4
        # parsed_4 = self.parser.parse_line(line_instruction, 4)

        self.assertEqual(parsed_1, instruction_form_1)
        self.assertEqual(parsed_2, instruction_form_2)
        self.assertEqual(parsed_3, instruction_form_3)
        # self.assertEqual(parsed_4, instruction_form_4)


##################
# Helper functions
##################
def get_comment(parser, comment):
    return ' '.join(parser.comment.parseString(comment, parseAll=True).asDict()['comment'])


def get_label(parser, label):
    return parser.label.parseString(label, parseAll=True).asDict()


def get_directive(parser, directive):
    return parser.directive.parseString(directive, parseAll=True).asDict()
