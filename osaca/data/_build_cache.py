#!/usr/bin/env python3
from glob import glob
import os.path
import sys
sys.path[0:0] = ['../..']

failed = False
try:
    from osaca.semantics.hw_model import MachineModel
except ModuleNotFoundError:
    print("Unable to import MachineModel, probably some dependency is not yet installed. SKIPPING. "
          "First run of OSACA may take a while to build caches, subsequent runs will be as fast as "
          "ever.")
    sys.exit()

print('Building cache: ', end='')
sys.stdout.flush()

# Iterating architectures
for f in glob(os.path.join(os.path.dirname(__file__), '*.yml')):
    MachineModel(path_to_yaml=f)
    print('.', end='')
    sys.stdout.flush()

# Iterating ISAs
for f in glob(os.path.join(os.path.dirname(__file__), 'isa/*.yml')):
    MachineModel(path_to_yaml=f)
    print('+', end='')
    sys.stdout.flush()

print()