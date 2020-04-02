#!/usr/bin/env python3
"""
Unit tests for DB interface
"""
import os
import unittest
from io import StringIO

import osaca.db_interface as dbi
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
        output = StringIO()
        # non-verbose
        sanity_check('csx', verbose=False, internet_check=False, output_file=output)
        sanity_check('tx2', verbose=False, internet_check=False, output_file=output)
        sanity_check('zen1', verbose=False, internet_check=False, output_file=output)

        # verbose
        sanity_check('csx', verbose=True, internet_check=False, output_file=output)
        sanity_check('tx2', verbose=True, internet_check=False, output_file=output)
        sanity_check('zen1', verbose=True, internet_check=False, output_file=output)

    def test_ibench_import(self):
        # only check import without dumping the DB file (takes too much time)
        with open(self._find_file('ibench_import_x86.dat')) as input_file:
            input_data = input_file.readlines()
            entries = dbi._get_ibench_output(input_data, 'x86')
            self.assertEqual(len(entries), 3)
            for _, e in entries.items():
                self.assertIsNotNone(e['throughput'])
                self.assertIsNotNone(e['latency'])
        with open(self._find_file('ibench_import_aarch64.dat')) as input_file:
            input_data = input_file.readlines()
            entries = dbi._get_ibench_output(input_data, 'aarch64')
            self.assertEqual(len(entries), 4)
            for _, e in entries.items():
                self.assertIsNotNone(e['throughput'])
                self.assertIsNotNone(e['latency'])

    def test_asmbench_import(self):
        # only check import without dumping the DB file (takes too much time)
        with open(self._find_file('asmbench_import_x86.dat')) as input_file:
            input_data = input_file.readlines()
            entries = dbi._get_asmbench_output(input_data, 'x86')
            self.assertEqual(len(entries), 3)
            for _, e in entries.items():
                self.assertIsNotNone(e['throughput'])
                self.assertIsNotNone(e['latency'])
        with open(self._find_file('asmbench_import_aarch64.dat')) as input_file:
            input_data = input_file.readlines()
            entries = dbi._get_asmbench_output(input_data, 'aarch64')
            self.assertEqual(len(entries), 4)
            for _, e in entries.items():
                self.assertIsNotNone(e['throughput'])
                self.assertIsNotNone(e['latency'])
            # remove empty line => no import since broken format
            del input_data[3]
            entries = dbi._get_asmbench_output(input_data, 'aarch64')
            self.assertEqual(len(entries), 0)
        with self.assertRaises(ValueError):
            dbi.import_benchmark_output(
                'csx', 'invalid_bench_type', self._find_file('asmbench_import_x86.dat')
            )
        with self.assertRaises(AssertionError):
            dbi.import_benchmark_output('csx', 'ibench', 'invalid_file')

    def test_online_scraping(self):
        # addpd -- suspicious instruction, normal URL
        instr_1 = ['addpd', (True, '(r) (r,w)')]
        self.assertEqual(dbi._scrape_from_felixcloutier(instr_1[0]), instr_1[1])
        # movpd -- not suspicious,
        instr_2 = ['movapd', (False, '(r) (w)')]
        self.assertEqual(dbi._scrape_from_felixcloutier(instr_2[0]), instr_2[1])
        # vfmadd132pd -- only in combined view with 213/231.
        # No 2-operand version, therefore, empty string
        instr_3 = ['vfmadd132pd', (True, '')]
        self.assertEqual(dbi._scrape_from_felixcloutier(instr_3[0]), instr_3[1])

    ##################
    # Helper functions
    ##################
    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'test_files', name)
        assert os.path.exists(name)
        return name


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDBInterface)
    unittest.TextTestRunner(verbosity=2).run(suite)
