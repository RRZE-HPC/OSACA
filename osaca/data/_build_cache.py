#!/usr/bin/env python3
from glob import glob
import os.path
import sys
sys.path[0:0] = ['../..']

from osaca.semantics.hw_model import MachineModel

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