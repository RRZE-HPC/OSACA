#!/usr/bin/env python3
"""
Unit tests for ARMv8 AArch64 assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import AttrDict, ParserAArch64v81


class TestParserAArch64v81(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = ParserAArch64v81()
        with open(self._find_file('triad_arm_iaca.s')) as f:
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
        self.assertEqual(self._get_label(self.parser, 'main:').name, 'main')
        self.assertEqual(self._get_label(self.parser, '..B1.10:').name, '..B1.10')
        self.assertEqual(self._get_label(self.parser, '.2.3_2_pack.3:').name, '.2.3_2_pack.3')
        self.assertEqual(self._get_label(self.parser, '.L1:\t\t\t//label1').name, '.L1')
        self.assertEqual(
            ' '.join(self._get_label(self.parser, '.L1:\t\t\t//label1').comment), 'label1'
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, '\t.cfi_startproc')

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, '\t.text').name, 'text')
        self.assertEqual(len(self._get_directive(self.parser, '\t.text').parameters), 0)
        self.assertEqual(self._get_directive(self.parser, '\t.align\t16,0x90').name, 'align')
        self.assertEqual(len(self._get_directive(self.parser, '\t.align\t16,0x90').parameters), 2)
        self.assertEqual(
            self._get_directive(self.parser, '\t.align\t16,0x90').parameters[1], '0x90'
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
        instr7 = 'fadd    v17.2d, v16.2d, v1.2d'

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        parsed_7 = self.parser.parse_instruction(instr7)

        self.assertEqual(parsed_1.instruction, 'vcvt.F32.S32')
        self.assertEqual(parsed_1.operands[0].register.name, '1')
        self.assertEqual(parsed_1.operands[0].register.prefix, 'w')
        self.assertEqual(parsed_1.operands[1].register.name, '2')
        self.assertEqual(parsed_1.operands[1].register.prefix, 'w')
        self.assertEqual(parsed_1.comment, '12.27')

        self.assertEqual(parsed_2.instruction, 'b.lo')
        self.assertEqual(parsed_2.operands[0].identifier.name, '..B1.4')
        self.assertEqual(len(parsed_2.operands), 1)
        self.assertIsNone(parsed_2.comment)

        self.assertEqual(parsed_3.instruction, 'mov')
        self.assertEqual(parsed_3.operands[0].register.name, '2')
        self.assertEqual(parsed_3.operands[0].register.prefix, 'x')
        self.assertEqual(parsed_3.operands[1].immediate.value, '0x222')
        self.assertEqual(parsed_3.comment, 'NOT IACA END')

        self.assertEqual(parsed_4.instruction, 'str')
        self.assertIsNone(parsed_4.operands[1].memory.offset)
        self.assertEqual(parsed_4.operands[1].memory.base.name, 'sp')
        self.assertEqual(parsed_4.operands[1].memory.base.prefix, 'x')
        self.assertEqual(parsed_4.operands[1].memory.index.name, '1')
        self.assertEqual(parsed_4.operands[1].memory.index.prefix, 'x')
        self.assertEqual(parsed_4.operands[1].memory.scale, 16)
        self.assertEqual(parsed_4.operands[0].register.name, '28')
        self.assertEqual(parsed_4.operands[0].register.prefix, 'x')
        self.assertEqual(parsed_4.comment, '12.9')

        self.assertEqual(parsed_5.instruction, 'ldr')
        self.assertEqual(parsed_5.operands[0].register.name, '0')
        self.assertEqual(parsed_5.operands[0].register.prefix, 'x')
        self.assertEqual(parsed_5.operands[1].memory.offset.identifier.name, 'q2c')
        self.assertEqual(parsed_5.operands[1].memory.offset.identifier.relocation,
                         ':got_lo12:')
        self.assertEqual(parsed_5.operands[1].memory.base.name, '0')
        self.assertEqual(parsed_5.operands[1].memory.base.prefix, 'x')
        self.assertIsNone(parsed_5.operands[1].memory.index)
        self.assertEqual(parsed_5.operands[1].memory.scale, 1)

        self.assertEqual(parsed_6.instruction, 'adrp')
        self.assertEqual(parsed_6.operands[0].register.name, '0')
        self.assertEqual(parsed_6.operands[0].register.prefix, 'x')
        self.assertEqual(parsed_6.operands[1].identifier.relocation, ':got:')
        self.assertEqual(parsed_6.operands[1].identifier.name, 'visited')

        self.assertEqual(parsed_7.instruction, 'fadd')
        self.assertEqual(parsed_7.operands[0].register.name, '17')
        self.assertEqual(parsed_7.operands[0].register.prefix, 'v')
        self.assertEqual(parsed_7.operands[0].register.lanes, '2')
        self.assertEqual(parsed_7.operands[0].register.shape, 'd')
        self.assertEqual(self.parser.get_full_reg_name(parsed_7.operands[2].register),
                         'v1.2d')

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
            'operands': [],
            'directive': None,
            'comment': '-- Begin main',
            'label': None,
            'line': '// -- Begin  main',
            'line_number': 1,
        }

        instruction_form_2 = {
            'instruction': None,
            'operands': [],
            'directive': None,
            'comment': '=>This Inner Loop Header: Depth=1',
            'label': '.LBB0_1',
            'line': '.LBB0_1:              // =>This Inner Loop Header: Depth=1',
            'line_number': 2,
        }
        instruction_form_3 = {
            'instruction': None,
            'operands': [],
            'directive': {'name': 'cfi_def_cfa', 'parameters': ['w29', '-16']},
            'comment': None,
            'label': None,
            'line': '.cfi_def_cfa w29, -16',
            'line_number': 3,
        }
        instruction_form_4 = {
            'instruction': 'ldr',
            'operands': [
                {'register': {'prefix': 's', 'name': '0'}},
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
                        'scale': 4,
                    }
                },
            ],
            'directive': None,
            'comment': '= <<2',
            'label': None,
            'line': 'ldr s0, [x11, w10, sxtw #2]\t\t// = <<2',
            'line_number': 4,
        }
        instruction_form_5 = {
            'instruction': 'prfm',
            'operands': [
                {'prfop': {'type': ['PLD'], 'target': ['L1'], 'policy': ['KEEP']}},
                {
                    'memory': {
                        'offset': {'value': '2048'},
                        'base': {'prefix': 'x', 'name': '26'},
                        'index': None,
                        'scale': 1,
                    }
                },
            ],
            'directive': None,
            'comment': 'HPL',
            'label': None,
            'line': 'prfm    pldl1keep, [x26, #2048] //HPL',
            'line_number': 5,
        }
        instruction_form_6 = {
            'instruction': 'stp',
            'operands': [
                {'register': {'prefix': 'x', 'name': '29'}},
                {'register': {'prefix': 'x', 'name': '30'}},
                {
                    'memory': {
                        'offset': {'value': '-16'},
                        'base': {'name': 'sp', 'prefix': 'x'},
                        'index': None,
                        'scale': 1,
                        'pre_indexed': True,
                    }
                },
            ],
            'directive': None,
            'comment': None,
            'label': None,
            'line': 'stp x29, x30, [sp, #-16]!',
            'line_number': 6,
        }
        instruction_form_7 = {
            'instruction': 'ldp',
            'operands': [
                {'register': {'prefix': 'q', 'name': '2'}},
                {'register': {'prefix': 'q', 'name': '3'}},
                {
                    'memory': {
                        'offset': None,
                        'base': {'prefix': 'x', 'name': '11'},
                        'index': None,
                        'scale': 1,
                        'post_indexed': {'value': '64'},
                    }
                },
            ],
            'directive': None,
            'comment': None,
            'label': None,
            'line': 'ldp q2, q3, [x11], #64',
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
        self.assertEqual(parsed[0].line_number, 1)
        self.assertEqual(len(parsed), 645)

    def test_normalize_imd(self):
        imd_decimal_1 = {'value': '79'}
        imd_hex_1 = {'value': '0x4f'}
        imd_decimal_2 = {'value': '8'}
        imd_hex_2 = {'value': '0x8'}
        imd_float_11 = {'float': {'mantissa': '0.79', 'e_sign': '+', 'exponent': '2'}}
        imd_float_12 = {'float': {'mantissa': '790.0', 'e_sign': '-', 'exponent': '1'}}
        imd_double_11 = {'double': {'mantissa': '0.79', 'e_sign': '+', 'exponent': '2'}}
        imd_double_12 = {'double': {'mantissa': '790.0', 'e_sign': '-', 'exponent': '1'}}
        identifier = {'identifier': {'name': '..B1.4'}}

        value1 = self.parser.normalize_imd(imd_decimal_1)
        self.assertEqual(value1, self.parser.normalize_imd(imd_hex_1))
        self.assertEqual(
            self.parser.normalize_imd(imd_decimal_2), self.parser.normalize_imd(imd_hex_2)
        )
        self.assertEqual(self.parser.normalize_imd(imd_float_11), value1)
        self.assertEqual(self.parser.normalize_imd(imd_float_12), value1)
        self.assertEqual(self.parser.normalize_imd(imd_double_11), value1)
        self.assertEqual(self.parser.normalize_imd(imd_double_12), value1)
        self.assertEqual(self.parser.normalize_imd(identifier), identifier)

    def test_multiple_regs(self):
        instr_range = 'PUSH {r5-r7}'
        reg_range = AttrDict({
            'register': {
                'range': [
                    {'prefix': 'r', 'name': '5'},
                    {'prefix': 'r', 'name': '7'}
                ],
                'index': None
            }
        })
        instr_list = 'POP {r5, r7, r9}'
        reg_list = AttrDict({
            'register': {
                'list': [
                    {'prefix': 'r', 'name': '5'},
                    {'prefix': 'r', 'name': '7'},
                    {'prefix': 'r', 'name': '9'}
                ],
                'index': None
            }
        })
        prange = self.parser.parse_line(instr_range)
        plist = self.parser.parse_line(instr_list)

        self.assertEqual(prange.operands[0], reg_range)
        self.assertEqual(plist.operands[0], reg_list)

    def test_reg_dependency(self):
        reg_1_1 = AttrDict({'prefix': 'b', 'name': '1'})
        reg_1_2 = AttrDict({'prefix': 'h', 'name': '1'})
        reg_1_3 = AttrDict({'prefix': 's', 'name': '1'})
        reg_1_4 = AttrDict({'prefix': 'd', 'name': '1'})
        reg_1_4 = AttrDict({'prefix': 'q', 'name': '1'})
        reg_2_1 = AttrDict({'prefix': 'w', 'name': '2'})
        reg_2_2 = AttrDict({'prefix': 'x', 'name': '2'})
        reg_v1_1 = AttrDict({'prefix': 'v', 'name': '11', 'lanes': '16', 'shape': 'b'})
        reg_v1_2 = AttrDict({'prefix': 'v', 'name': '11', 'lanes': '8', 'shape': 'h'})
        reg_v1_3 = AttrDict({'prefix': 'v', 'name': '11', 'lanes': '4', 'shape': 's'})
        reg_v1_4 = AttrDict({'prefix': 'v', 'name': '11', 'lanes': '2', 'shape': 'd'})

        reg_b5 = AttrDict({'prefix': 'b', 'name': '5'})
        reg_q15 = AttrDict({'prefix': 'q', 'name': '15'})
        reg_v10 = AttrDict({'prefix': 'v', 'name': '10', 'lanes': '2', 'shape': 's'})
        reg_v20 = AttrDict({'prefix': 'v', 'name': '20', 'lanes': '2', 'shape': 'd'})

        reg_1 = [reg_1_1, reg_1_2, reg_1_3, reg_1_4]
        reg_2 = [reg_2_1, reg_2_2]
        reg_v = [reg_v1_1, reg_v1_2, reg_v1_3, reg_v1_4]
        reg_others = [reg_b5, reg_q15, reg_v10, reg_v20]
        regs = reg_1 + reg_2 + reg_v + reg_others

        # test each register against each other
        for ri in reg_1:
            for rj in regs:
                assert_value = True if rj in reg_1 else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_2:
            for rj in regs:
                assert_value = True if rj in reg_2 else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_v:
            for rj in regs:
                assert_value = True if rj in reg_v else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_others:
            for rj in regs:
                assert_value = True if rj == ri else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)

    ##################
    # Helper functions
    ##################
    def _get_comment(self, parser, comment):
        return ' '.join(
            AttrDict.convert_dict(
                parser.process_operand(parser.comment.parseString(comment, parseAll=True).asDict())
            ).comment
        )

    def _get_label(self, parser, label):
        return AttrDict.convert_dict(
            parser.process_operand(parser.label.parseString(label, parseAll=True).asDict())
        ).label

    def _get_directive(self, parser, directive):
        return AttrDict.convert_dict(
            parser.process_operand(parser.directive.parseString(directive, parseAll=True).asDict())
        ).directive

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'test_files', name)
        assert os.path.exists(name)
        return name


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserAArch64v81)
    unittest.TextTestRunner(verbosity=2).run(suite)
