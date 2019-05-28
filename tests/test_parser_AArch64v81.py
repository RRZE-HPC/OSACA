#!/usr/bin/env python3
"""
Unit tests for ARMv8 AArch64 assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import ParserAArch64v81


class TestParserAArch64v81(unittest.TestCase):
    def setUp(self):
        self.parser = ParserAArch64v81()
        with open(self._find_file('triad-arm-iaca.s')) as f:
            self.triad_code = f.read()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(self._get_comment(self.parser, '// some comments'), 'some comments')
        self.assertEqual(
            self._get_comment(self.parser, '\t\t//AA BB CC \t end \t'), 'AA BB CC end'
        )
        self.assertEqual(
            self._get_comment(self.parser, '\t//// comment //// comment'),
            '// comment //// comment',
        )

    def test_label_parser(self):
        self.assertEqual(self._get_label(self.parser, 'main:')['name'], 'main')
        self.assertEqual(self._get_label(self.parser, '..B1.10:')['name'], '..B1.10')
        self.assertEqual(self._get_label(self.parser, '.2.3_2_pack.3:')['name'], '.2.3_2_pack.3')
        self.assertEqual(self._get_label(self.parser, '.L1:\t\t\t//label1')['name'], '.L1')
        self.assertEqual(
            ' '.join(self._get_label(self.parser, '.L1:\t\t\t//label1')['comment']), 'label1'
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
            self._get_directive(self.parser, '        .byte 100,103,144       //IACA START')[
                'name'
            ],
            'byte',
        )
        self.assertEqual(
            self._get_directive(self.parser, '        .byte 100,103,144       //IACA START')[
                'parameters'
            ][2],
            '144',
        )
        self.assertEqual(
            ' '.join(
                self._get_directive(self.parser, '        .byte 100,103,144       //IACA START')[
                    'comment'
                ]
            ),
            'IACA START',
        )

    def test_parse_instruction(self):
        instr1 = '\t\tvcvt.F32.S32 w1, w2\t\t\t//12.27'
        instr2 = 'b.lo        ..B1.4 \t'
        instr3 = '        mov x2,#0x222          //NOT IACA END'
        instr4 = 'str x28, [sp, x1, lsl #4] //12.9'
        instr5 = 'ldr x0, [x0, #:got_lo12:q2c]'
        instr6 = 'adrp    x0, :got:visited'

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)

        self.assertEqual(parsed_1['instruction'], 'vcvt.F32.S32')
        self.assertEqual(parsed_1['operands']['destination'][0]['register']['name'], '1')
        self.assertEqual(parsed_1['operands']['destination'][0]['register']['prefix'], 'w')
        self.assertEqual(parsed_1['operands']['source'][0]['register']['name'], '2')
        self.assertEqual(parsed_1['operands']['source'][0]['register']['prefix'], 'w')
        self.assertEqual(parsed_1['comment'], '12.27')

        self.assertEqual(parsed_2['instruction'], 'b.lo')
        self.assertEqual(parsed_2['operands']['destination'][0]['identifier']['name'], '..B1.4')
        self.assertEqual(len(parsed_2['operands']['source']), 0)
        self.assertIsNone(parsed_2['comment'])

        self.assertEqual(parsed_3['instruction'], 'mov')
        self.assertEqual(parsed_3['operands']['destination'][0]['register']['name'], '2')
        self.assertEqual(parsed_3['operands']['destination'][0]['register']['prefix'], 'x')
        self.assertEqual(parsed_3['operands']['source'][0]['immediate']['value'], '0x222')
        self.assertEqual(parsed_3['comment'], 'NOT IACA END')

        self.assertEqual(parsed_4['instruction'], 'str')
        self.assertIsNone(parsed_4['operands']['destination'][0]['memory']['offset'])
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['base']['name'], 'sp')
        self.assertIsNone(parsed_4['operands']['destination'][0]['memory']['base']['prefix'])
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['index']['name'], '1')
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['index']['prefix'], 'x')
        self.assertEqual(parsed_4['operands']['destination'][0]['memory']['scale'], '16')
        self.assertEqual(parsed_4['operands']['source'][0]['register']['name'], '28')
        self.assertEqual(parsed_4['operands']['source'][0]['register']['prefix'], 'x')
        self.assertEqual(parsed_4['comment'], '12.9')

        self.assertEqual(parsed_5['instruction'], 'ldr')
        self.assertEqual(parsed_5['operands']['destination'][0]['register']['name'], '0')
        self.assertEqual(parsed_5['operands']['destination'][0]['register']['prefix'], 'x')
        self.assertEqual(
            parsed_5['operands']['source'][0]['memory']['offset']['identifier']['name'], 'q2c'
        )
        self.assertEqual(
            parsed_5['operands']['source'][0]['memory']['offset']['identifier']['relocation'],
            ':got_lo12:',
        )
        self.assertEqual(parsed_5['operands']['source'][0]['memory']['base']['name'], '0')
        self.assertEqual(parsed_5['operands']['source'][0]['memory']['base']['prefix'], 'x')
        self.assertIsNone(parsed_5['operands']['source'][0]['memory']['index'])
        self.assertEqual(parsed_5['operands']['source'][0]['memory']['scale'], '1')

        self.assertEqual(parsed_6['instruction'], 'adrp')
        self.assertEqual(parsed_6['operands']['destination'][0]['register']['name'], '0')
        self.assertEqual(parsed_6['operands']['destination'][0]['register']['prefix'], 'x')
        self.assertEqual(parsed_6['operands']['source'][0]['identifier']['relocation'], ':got:')
        self.assertEqual(parsed_6['operands']['source'][0]['identifier']['name'], 'visited')

    def test_parse_line(self):
        line_comment = '// -- Begin  main'
        line_label = '.LBB0_1:              // =>This Inner Loop Header: Depth=1'
        line_directive = '\t.cfi_def_cfa w29, -16'
        line_instruction = '\tldr s0, [x11, w10, sxtw #2]\t\t// = <<2'
        line_prefetch = 'prfm    pldl1keep, [x26, #2048] //HPL'
        line_preindexed = 'stp x29, x30, [sp, #-16]!'
        line_postindexed = 'ldp q2, q3, [x11], #64'

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
            'comment': '=>This Inner Loop Header: Depth=1',
            'label': '.LBB0_1',
            'line_number': 2,
        }
        instruction_form_3 = {
            'instruction': None,
            'operands': None,
            'directive': {'name': 'cfi_def_cfa', 'parameters': ['w29', '-16']},
            'comment': None,
            'label': None,
            'line_number': 3,
        }
        instruction_form_4 = {
            'instruction': 'ldr',
            'operands': {
                'source': [
                    {
                        'memory': {
                            'offset': None,
                            'base': {'prefix': 'x', 'name': '11'},
                            'index': {
                                'prefix': 'w',
                                'name': '10',
                                'shift_op': 'sxtw',
                                'shift': {'value': '2'},
                            },
                            'scale': '4',
                        }
                    }
                ],
                'destination': [{'register': {'prefix': 's', 'name': '0'}}],
            },
            'directive': None,
            'comment': '= <<2',
            'label': None,
            'line_number': 4,
        }
        instruction_form_5 = {
            'instruction': 'prfm',
            'operands': {
                'source': [
                    {
                        'memory': {
                            'offset': {'value': '2048'},
                            'base': {'prefix': 'x', 'name': '26'},
                            'index': None,
                            'scale': '1',
                        }
                    }
                ],
                'destination': [
                    {'prfop': {'type': ['PLD'], 'target': ['L1'], 'policy': ['KEEP']}}
                ],
            },
            'directive': None,
            'comment': 'HPL',
            'label': None,
            'line_number': 5,
        }
        instruction_form_6 = {
            'instruction': 'stp',
            'operands': {
                'source': [
                    {'register': {'prefix': 'x', 'name': '29'}},
                    {'register': {'prefix': 'x', 'name': '30'}}
                ],
                'destination': [
                    {
                        'memory': {
                            'offset': {'value': '-16'},
                            'base': {'name': 'sp', 'prefix': None},
                            'index': None,
                            'scale': '1',
                            'pre-indexed': True
                        }
                    }
                ],
            },
            'directive': None,
            'comment': None,
            'label': None,
            'line_number': 6
        }
        instruction_form_7 = {
            'instruction': 'ldp',
            'operands': {
                'source': [
                    {
                        'memory': {
                            'offset': None,
                            'base': {'prefix': 'x', 'name': '11'},
                            'index': None,
                            'scale': '1',
                            'post-indexed': {'value': '64'},
                        }
                    }
                ],
                'destination': [
                    {'register': {'prefix': 'q', 'name': '2'}},
                    {'register': {'prefix': 'q', 'name': '3'}},
                ],
            },
            'directive': None,
            'comment': None,
            'label': None,
            'line_number': 7,
        }
        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        parsed_4 = self.parser.parse_line(line_instruction, 4)
        parsed_5 = self.parser.parse_line(line_prefetch, 5)
        parsed_6 = self.parser.parse_line(line_preindexed, 6)
        parsed_7 = self.parser.parse_line(line_postindexed, 7)

        self.assertEqual(parsed_1, instruction_form_1)
        self.assertEqual(parsed_2, instruction_form_2)
        self.assertEqual(parsed_3, instruction_form_3)
        self.assertEqual(parsed_4, instruction_form_4)
        self.assertEqual(parsed_5, instruction_form_5)
        self.assertEqual(parsed_6, instruction_form_6)
        self.assertEqual(parsed_7, instruction_form_7)

    def test_parse_file(self):
        parsed = self.parser.parse_file(self.triad_code)
        self.assertEqual(parsed[0]['line_number'], 1)
        self.assertEqual(len(parsed), 645)

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserAArch64v81)
    unittest.TextTestRunner(verbosity=2).run(suite)
