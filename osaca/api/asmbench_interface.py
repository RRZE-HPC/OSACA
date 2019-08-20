#!/usr/bin/env python3

import os


class AsmBenchAPI(object):
    def __init__(self, isa):
        # TODO
        self.isa = isa.lower()

    def create_ubenchmark(self):
        # TODO
        if self.isa == 'aarch64':
            self.create_ubench_aarch64()
        elif self.isa == 'x86':
            self.create_ubench_x86()

    def import_asmbench_output(self, filepath):
        # TODO
        assert os.path.exists(filepath)
        raise NotImplementedError

    def create_ubench_aarch(self):
        # TODO
        raise NotImplementedError

    def create_ubench_x86(self):
        # TODO
        raise NotImplementedError
