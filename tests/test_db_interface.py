#!/usr/bin/env python3
"""
Unit tests for DB interface
"""

import copy
import os
import sys
import unittest

from osaca.api import add_entries_to_db, add_entry_to_db, sanity_check
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
        self.entry_vulcan = sample_entry.copy()
        self.entry_zen1 = sample_entry.copy()

        self.entry_csx['port_pressure'] = [1.25, 0, 1.25, 0.5, 0.5, 0.5, 0.5, 0, 1.25, 1.25, 0]
        self.entry_vulcan['port_pressure'] = [2.5, 2.5, 0, 0, 0.5, 0.5]
        del self.entry_vulcan['operands'][1]['name']
        self.entry_vulcan['operands'][1]['prefix'] = 'x'
        self.entry_zen1['port_pressure'] = [1, 1, 1, 1, 0, 1, 0, 0, 0, 0.5, 1, 0.5, 1]

    @classmethod
    def tearDownClass(self):
        if sys.exc_info() == (None, None, None):
            # Test successful, remove DB entries
            test_archs = {'csx': 22, 'vulcan': 24, 'zen1': 22}
            for arch in test_archs:
                lines = []
                with open(os.path.expanduser('~/.osaca/data/' + arch + '.yml'), 'r') as f:
                    lines = f.readlines()
                with open(os.path.expanduser('~/.osaca/data/' + arch + '.yml'), 'w') as f:
                    f.writelines([line for line in lines[:-1 * test_archs[arch]]])

    ###########
    # Tests
    ###########

    def test_add_single_entry(self):
        num_entries_csx = len(MachineModel('csx')['instruction_forms'])
        num_entries_vulcan = len(MachineModel('vulcan')['instruction_forms'])
        num_entries_zen1 = len(MachineModel('zen1')['instruction_forms'])

        add_entry_to_db('csx', self.entry_csx)
        add_entry_to_db('vulcan', self.entry_vulcan)
        add_entry_to_db('zen1', {'name': 'empty_operation'})

        num_entries_csx = len(MachineModel('csx')['instruction_forms']) - num_entries_csx
        num_entries_vulcan = len(MachineModel('vulcan')['instruction_forms']) - num_entries_vulcan
        num_entries_zen1 = len(MachineModel('zen1')['instruction_forms']) - num_entries_zen1

        self.assertEqual(num_entries_csx, 1)
        self.assertEqual(num_entries_vulcan, 1)
        self.assertEqual(num_entries_zen1, 1)

    def test_invalid_add(self):
        entry = {}
        with self.assertRaises(ValueError):
            add_entry_to_db('csx', entry)
        add_entries_to_db('csx', [entry])

    def test_add_multiple_entries(self):
        num_entries_csx = len(MachineModel('csx')['instruction_forms'])
        num_entries_vulcan = len(MachineModel('vulcan')['instruction_forms'])
        num_entries_zen1 = len(MachineModel('zen1')['instruction_forms'])

        entries_csx, entries_vulcan, entries_zen1 = [], [], []
        for i in range(2):
            self.entry_csx['name'] += '-'
            self.entry_vulcan['name'] += '-'
            self.entry_zen1['name'] += '-'
            entries_csx.append(copy.deepcopy(self.entry_csx))
            entries_vulcan.append(copy.deepcopy(self.entry_vulcan))
            entries_zen1.append(copy.deepcopy(self.entry_zen1))

        entries_csx[1] = {'name': entries_csx[1]['name']}

        add_entries_to_db('csx', entries_csx)
        add_entries_to_db('vulcan', entries_vulcan)
        add_entries_to_db('zen1', entries_zen1)

        num_entries_csx = len(MachineModel('csx')['instruction_forms']) - num_entries_csx
        num_entries_vulcan = len(MachineModel('vulcan')['instruction_forms']) - num_entries_vulcan
        num_entries_zen1 = len(MachineModel('zen1')['instruction_forms']) - num_entries_zen1

        self.assertEqual(num_entries_csx, 2)
        self.assertEqual(num_entries_vulcan, 2)
        self.assertEqual(num_entries_zen1, 2)

    def test_sanity_check(self):
        # non-verbose
        sanity_check('csx', verbose=False)
        sanity_check('vulcan', verbose=False)
        sanity_check('zen1', verbose=False)
        # verbose
        sanity_check('csx', verbose=True)
        sanity_check('vulcan', verbose=True)
        sanity_check('zen1', verbose=True)

    ##################
    # Helper functions
    ##################


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDBInterface)
    unittest.TextTestRunner(verbosity=2).run(suite)
