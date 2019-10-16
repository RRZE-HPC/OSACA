#!/usr/bin/env python3
"""
Unit tests for DB interface
"""

import unittest

from osaca.db_interface import sanity_check
from osaca.semantics import MachineModel


class TestDBInterface(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        sample_entry = {
            'name': 'DoItRightAndDoItFast',
            'operands': [
                {'class': 'memory', 'offset': 'imd', 'base': 'gpr', 'index': 'gpr', 'scale': 8},
                {'class': 'register', 'name': 'xmm'},
            ],
            'throughput': 1.25,
            'latency': 125,
            'uops': 6,
        }
        self.entry_csx = sample_entry.copy()
        self.entry_tx2 = sample_entry.copy()
        self.entry_zen1 = sample_entry.copy()

        # self.entry_csx['port_pressure'] = [1.25, 0, 1.25, 0.5, 0.5, 0.5, 0.5, 0, 1.25, 1.25, 0]
        self.entry_csx['port_pressure'] = [[5, '0156'], [1, '23'], [1, ['2D', '3D']]]
        # self.entry_tx2['port_pressure'] = [2.5, 2.5, 0, 0, 0.5, 0.5]
        self.entry_tx2['port_pressure'] = [[5, '01'], [1, '45']]
        del self.entry_tx2['operands'][1]['name']
        self.entry_tx2['operands'][1]['prefix'] = 'x'
        # self.entry_zen1['port_pressure'] = [1, 1, 1, 1, 0, 1, 0, 0, 0, 0.5, 1, 0.5, 1]
        self.entry_zen1['port_pressure'] = [[4, '0123'], [1, '4'], [1, '89'], [2, ['8D', '9D']]]

    ###########
    # Tests
    ###########

    def test_add_single_entry(self):
        mm_csx = MachineModel('csx')
        mm_tx2 = MachineModel('tx2')
        mm_zen1 = MachineModel('zen1')
        num_entries_csx = len(mm_csx['instruction_forms'])
        num_entries_tx2 = len(mm_tx2['instruction_forms'])
        num_entries_zen1 = len(mm_zen1['instruction_forms'])

        mm_csx.set_instruction_entry(self.entry_csx)
        mm_tx2.set_instruction_entry(self.entry_tx2)
        mm_zen1.set_instruction_entry({'name': 'empty_operation'})

        num_entries_csx = len(mm_csx['instruction_forms']) - num_entries_csx
        num_entries_tx2 = len(mm_tx2['instruction_forms']) - num_entries_tx2
        num_entries_zen1 = len(mm_zen1['instruction_forms']) - num_entries_zen1

        self.assertEqual(num_entries_csx, 1)
        self.assertEqual(num_entries_tx2, 1)
        self.assertEqual(num_entries_zen1, 1)

    def test_invalid_add(self):
        entry = {}
        with self.assertRaises(KeyError):
            MachineModel('csx').set_instruction_entry(entry)
        with self.assertRaises(TypeError):
            MachineModel('csx').set_instruction()

    def test_sanity_check(self):
        # non-verbose
        sanity_check('csx', verbose=False)
        sanity_check('tx2', verbose=False)
        sanity_check('zen1', verbose=False)
        # verbose
        sanity_check('csx', verbose=True)
        sanity_check('tx2', verbose=True)
        sanity_check('zen1', verbose=True)

    ##################
    # Helper functions
    ##################


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDBInterface)
    unittest.TextTestRunner(verbosity=2).run(suite)
