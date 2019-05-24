#!/usr/bin/env python3
"""
Unit tests for x86 AT&T assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import ParserX86ATT


class TestParserX86ATT(unittest.TestCase):
    def setUp(self):
        self.parser = ParserX86ATT()
        with open(self._find_file('triad-x86-iaca.s')) as f:
            self.triad_code = f.read()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(self._get_comment(self.parser, '# some comments'), 'some comments')
        self.assertEqual(self._get_comment(self.parser, '\t\t#AA BB CC \t end \t'), 'AA BB CC end')
        self.assertEqual(
            self._get_comment(self.parser, '\t## comment ## comment'), '# comment ## comment'
        )

    def test_label_parser(self):
        self.assertEqual(self._get_label(self.parser, 'main:')['name'], 'main')
        self.assertEqual(self._get_label(self.parser, '..B1.10:')['name'], '..B1.10')
        self.assertEqual(self._get_label(self.parser, '.2.3_2_pack.3:')['name'], '.2.3_2_pack.3')
        self.assertEqual(self._get_label(self.parser, '.L1:\t\t\t#label1')['name'], '.L1')
        self.assertEqual(
            ' '.join(self._get_label(self.parser, '.L1:\t\t\t#label1')['comment']), 'label1'
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, '\t.cfi_startproc')

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, '\t.text')['name'], 'text')
        self.assertEqual(len(self._get_directive(self.parser, '\t.text')['parameters']), 0)
        self.assertEqual(self._get_directive(self.parser, '\t.align\t16,0x90')['name'], 'align')
        self.assertEqual(
            len(self._get_directive(self.parser, '\t.align\t16,0x90')['parameters']), 2
        )
        self.assertEqual(
            self._get_directive(self.parser, '\t.align\t16,0x90')['parameters'][1], '0x90'
        )
        self.assertEqual(
            self._get_directive(self.parser, '        .byte 100,103,144       #IACA START')[
                'name'
            ],
            'byte',
        )
        self.assertEqual(
            self._get_directive(self.parser, '        .byte 100,103,144       #IACA START')[
                'parameters'
            ][2],
            '144',
        )
        self.assertEqual(
            ' '.join(
                self._get_directive(self.parser, '        .byte 100,103,144       #IACA START')[
                    'comment'
                ]
            ),
            'IACA START',
        )

    def test_parse_instruction(self):
        instr1 = '\t\tvcvtsi2ss %edx, %xmm2, %xmm2\t\t\t#12.27'
        instr2 = 'jb        ..B1.4 \t'
        instr3 = '        movl $222,%ebx          #IACA END'
        instr4 = 'vmovss    %xmm4, -4(%rsp,%rax,8) #12.9'
        instr5 = 'mov %ebx,var(,1)'
        instr6 = 'lea (,%rax,8),%rbx'

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)

        self.assertEqual(parsed_1['instruction'], 'vcvtsi2ss')
        self.assertEqual(parsed_1['operands']['destination'][0]['register']['name'], 'xmm2')
        self.assertEqual(parsed_1['operands']['source'][0]['register']['name'], 'edx')
        self.assertEqual(parsed_1['comment'], '12.27')

        self.assertEqual(parsed_2['instruction'], 'jb')
        self.assertEqual(parsed_2['operands']['destination'][0]['identifier']['name'], '..B1.4')
        self.assertEqual(len(parsed_2['operands']['source']), 0)
        self.assertIsNone(parsed_2['comment'])

        self.assertEqual(parsed_3['instruction'], 'movl')
        self.assertEqual(parsed_3['operands']['destination'][0]['register']['name'], 'ebx')
        self.assertEqual(parsed_3['operands']['source'][0]['immediate']['value'], '222')
        self.assertEqual(parsed_3['comment'], 'IACA END')

        self.assertEqual(parsed_4['instruction'], 'vmovss')
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['offset']['value'], '-4')
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['base']['name'], 'rsp')
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['index']['name'], 'rax')
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['scale'], '8')
        self.assertEqual(parsed_4['operands']['source'][0]['register']['name'], 'xmm4')
        self.assertEqual(parsed_4['comment'], '12.9')

        self.assertEqual(parsed_5['instruction'], 'mov')
        self.assertEqual(
            parsed_5['operands']['destination'][0]['memory']['offset']['identifier']['name'], 'var'
        )
        self.assertIsNone(parsed_5['operands']['destination'][0]['memory']['base'])
        self.assertIsNone(parsed_5['operands']['destination'][0]['memory']['index'])
        self.assertEqual(parsed_5['operands']['destination'][0]['memory']['scale'], '1')
        self.assertEqual(parsed_5['operands']['source'][0]['register']['name'], 'ebx')

        self.assertEqual(parsed_6['instruction'], 'lea')
        self.assertIsNone(parsed_6['operands']['source'][0]['memory']['offset'])
        self.assertIsNone(parsed_6['operands']['source'][0]['memory']['base'])
        self.assertEqual(parsed_6['operands']['source'][0]['memory']['index']['name'], 'rax')
        self.assertEqual(parsed_6['operands']['source'][0]['memory']['scale'], '8')
        self.assertEqual(parsed_6['operands']['destination'][0]['register']['name'], 'rbx')

    def test_parse_line(self):
        line_comment = '# -- Begin  main'
        line_label = '..B1.7:                         # Preds ..B1.6'
        line_directive = '\t\t.quad   .2.3_2__kmpc_loc_pack.2 #qed'
        line_instruction = '\t\tlea       2(%rax,%rax), %ecx #12.9'

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
            'comment': 'Preds ..B1.6',
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
        instruction_form_4 = {
            'instruction': 'lea',
            'operands': {
                'source': [
                    {
                        'memory': {
                            'offset': {'value': '2'},
                            'base': {'name': 'rax'},
                            'index': {'name': 'rax'},
                            'scale': '1',
                        }
                    }
                ],
                'destination': [{'register': {'name': 'ecx'}}],
            },
            'directive': None,
            'comment': '12.9',
            'label': None,
            'line_number': 4,
        }

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        parsed_4 = self.parser.parse_line(line_instruction, 4)

        self.assertEqual(parsed_1, instruction_form_1)
        self.assertEqual(parsed_2, instruction_form_2)
        self.assertEqual(parsed_3, instruction_form_3)
        self.assertEqual(parsed_4, instruction_form_4)

    def test_parse_file(self):
        parsed = self.parser.parse_file(self.triad_code)
        self.assertEqual(parsed[0]['line_number'], 1)
        self.assertEqual(len(parsed), 353)

    ##################
    # Helper functions
    ##################
    def _get_comment(self, parser, comment):
        return ' '.join(
            parser._process_operand(parser.comment.parseString(comment, parseAll=True).asDict())[
                'comment'
            ]
        )

    def _get_label(self, parser, label):
        return parser._process_operand(parser.label.parseString(label, parseAll=True).asDict())[
            'label'
        ]

    def _get_directive(self, parser, directive):
        return parser._process_operand(
            parser.directive.parseString(directive, parseAll=True).asDict()
        )['directive']

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'test_files', name)
        assert os.path.exists(name)
        return name


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserX86ATT)
    unittest.TextTestRunner(verbosity=2).run(suite)
