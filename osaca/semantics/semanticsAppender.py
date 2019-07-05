#!/usr/bin/env python3

import os

from .hw_model import MachineModel


class SemanticsAppender(object):
    def __init__(self, machine_model: MachineModel):
        self.machine_model = machine_model
        self._isa = machine_model.get_ISA()
        self._isa_model = MachineModel(path_to_yaml=self._find_file(self._isa))

    def _find_file(self, isa):
        data_dir = os.path.expanduser('~/.osaca/data/isa')
        name = os.path.join(data_dir, isa + '.yml')
        assert os.path.exists(name)
        return name

    # get parser result and assign operands to
    # - source
    # - destination
    # - source/destination

    # for this, have a default implementation and get exceptions from generic x86/AArch64 ISA file
    def assign_src_dst(self, instruction_form):
        # check if instruction form is in ISA yaml, otherwise apply standard operand assignment
        # (one dest, others source)
        isa_data = self._isa_model.get_instruction(
            instruction_form['name'], instruction_form['operands']
        )
        if isa_data is None:
            # no irregular operand structure, apply default
            # TODO
            pass
        else:
            # load src/dst structure from isa_data
            # TODO
            pass
        raise NotImplementedError
