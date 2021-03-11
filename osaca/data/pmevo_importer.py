#!/usr/bin/env python3
import os.path
import argparse
import math
import sys
import re
import json

from osaca.parser import get_parser
from osaca.semantics import MachineModel

from asmbench import op, bench


def build_bench_instruction(name, operands):
    # Converts an OSACA model instruction to an asmbench one.
    # Returns `None` in case something went wrong.
    asmbench_inst = name
    direction = 'dst'
    separator = ' '
    shift = ''
    for operand in operands:
        if operand['class'] == 'register' or operand['class'] == 'register_shift':
            if operand['prefix'] == 'x':
                shape = 'i64'
                constraint = 'r'
            elif operand['prefix'] == 's':
                shape = 'float'
                constraint = 'w'
            elif operand['prefix'] == 'd':
                shape = 'double'
                constraint = 'w'
            elif operand['prefix'] == 'v':
                constraint = 'w'
                if operand['shape'] == 'b':
                    shape = '<16 x i8>'
                elif operand['shape'] == 'h':
                    shape = '<8 x i16>'
                elif operand['shape'] == 's':
                    shape = '<4 x float>'
                elif operand['shape'] == 'd':
                    shape = '<2 x double>'
                else:
                    return None
            else:
                return None
            if operand['class'] == 'register_shift':
                shift = ', {}'.format(operand['shift_op'])
                if operand['shift'] != None:
                    shift += ' {}'.format(operand['shift'])
        elif operand['class'] == 'immediate' or operand['class'] == 'immediate_shift':
            shape = 'i32'
            # Different instructions have different ranges for literaly,
            # so need to pick something "reasonable" for each.
            if name in ['cmeq', 'cmge', 'cmgt', 'cmle', 'cmlt', 'fcmeq', 'fcmge', 'fcmgt', 'fcmle', 'fcmlt', 'fcmp']:
                constraint = '0'
            elif name in ['and', 'ands', 'eor', 'eors', 'orr', 'orrs']:
                constraint = '255'
            elif name in ['bfi', 'extr', 'sbfiz', 'sbfx', 'shl', 'sshr', 'ubfiz', 'ubfx', 'ushr']:
                constraint = '7'
            else:
                constraint = '42'
            if operand['class'] == 'immediate_shift':
                shift = ', {}'.format(operand['shift_op'])
                if operand['shift'] != None:
                    shift += ' {}'.format(operand['shift'])
        else:
            return None
        asmbench_inst += '{}{{{}:{}:{}}}{}'.format(separator, direction, shape, constraint, shift)
        direction = 'src'
        separator = ', '
    return asmbench_inst


def bench_instruction(name, operands):
    # Converts an OSACA model instruction to an asmbench one and benchmarks it.
    # Returned tuple may contain a `None` in case something went wrong.
    asmbench_inst = build_bench_instruction(name, operands)
    if asmbench_inst == None:
        return (None, None)
    return bench.bench_instructions([op.Instruction.from_string(asmbench_inst)])


def round_cycles(value):
    if value < 0.9:
        # Frequently found, so we might want to include them.
        # Measurements over-estimate a lot here, hence the high bound.
        return 0.5
    else:
        # Measurements usually over-estimate, so usually round down,
        # but still allow slightly smaller values.
        return float(math.floor(value + 0.1))


def operand_parse(op, state):
    # Parses an operand from an PMEvo instruction and emits an OSACA model one.
    # State object is used to keep track of types for future operands, e.g. literals.
    # Future invocations may also modify previously returned objects.
    parameter = {}

    memory_base = None

    if op.startswith('_((REG:'):
        parts = op.split('.')
        register = parts[0][7:-2]
        read_write, register_type, bits = register.split(':')

        parameter['class'] = 'register'
        if register_type == 'G':
            if bits == '32':
                parameter['prefix'] = 'r'
            elif bits == '64':
                parameter['prefix'] = 'x'
            else:
                raise ValueError("Invalid register bits for {} {}".format(register_type, bits))
        elif register_type == 'F':
            if bits == '32':
                parameter['prefix'] = 's'
                state['type'] = 'float'
            elif bits == '64':
                parameter['prefix'] = 'd'
                state['type'] = 'double'
            elif bits == '128':
                parameter['prefix'] = 'q'
            elif bits == 'VEC':
                vec_shape = parts[1]
                parameter['prefix'] = 'v'
                if vec_shape == '16b':
                    parameter['shape'] = 'b'
                elif vec_shape == '8h':
                    parameter['shape'] = 'h'
                elif vec_shape == '4s':
                    parameter['shape'] = 's'
                    state['type'] = 'float'
                elif vec_shape == '2d':
                    parameter['shape'] = 'd'
                    state['type'] = 'double'
                else:
                    raise ValueError("Invalid vector shape {}".format(vec_shape))
            else:
                raise ValueError("Invalid register bits for {} {}".format(register_type, bits))
        else:
            raise ValueError("Unknown register type {}".format(register_type))
    elif op.startswith('_[((MEM:'):
        bits = op[8:-2].split(':')[0]
        if bits == '64':
            state['memory_base'] = 'x'
        else:
            raise ValueError("Invalid register bits for MEM {}".format(bits))
        return None
    elif op.startswith('_((MIMM:'):
        bits = op[8:-3].split(':')[0]
        if bits == '16':
            parameter['class'] = 'memory'
            parameter['base'] = state['memory_base']
            parameter['offset'] = 'imd'
            parameter['index'] = '*'
            parameter['scale'] = '*'
            parameter['post-indexed'] = False
            parameter['pre-indexed'] = False
        else:
            raise ValueError("Invalid register bits for MEM {}".format(bits))
    elif re.fullmatch('_#?-?(0x)?[0-9a-f]+', op):
        parameter['class'] = 'immediate'
        parameter['imd'] = 'int'
    elif re.fullmatch('_#?-?[0-9]*\\.[0-9]*', op):
        parameter['class'] = 'immediate'
        parameter['imd'] = state['type']
    elif re.fullmatch('_((sxt|uxt)[bhw]|lsl|lsr|asr|rol|ror)(_[0-9]+)?', op):
        # split = op[1:].split('_')
        # shift_op = split[0]
        # shift = None
        # if len(split) >= 2:
        #     shift = split[1]
        # state['previous']['class'] += '_shift'
        # state['previous']['shift_op'] = shift_op
        # if shift != None:
        #     state['previous']['shift'] = shift
        # return None
        raise ValueError("Skipping instruction with shift operand: {}".format(op))
    else:
        raise ValueError("Unknown operand {}".format(op))

    state['previous'] = parameter
    return parameter


def port_convert(ports):
    # Try to merge repeated entries together and emit in OSACA's format.
    # FIXME: This does not handle having more than 10 ports.
    pressures = []
    previous = None
    cycles = 0

    for entry in ports:
        possible_ports = ''.join(entry)

        if possible_ports != previous:
            if previous != None:
                pressures.append([cycles, previous])
            previous = possible_ports
            cycles = 0

        cycles += 1

    if previous != None:
        pressures.append([cycles, previous])

    return pressures


def throughput_guess(ports):
    # Minimum amount of possible ports per cycle should determine throughput
    # to some degree of accuracy. (THIS IS *NOT* ALWAYS TRUE!)
    bottleneck_ports = min(map(lambda it: len(it), ports))
    return float(len(ports)) / bottleneck_ports


def latency_guess(ports):
    # Each entry in the ports array equates to one cycle on any of the ports.
    # So this is about as good as it is going to get.
    return float(len(ports))


def extract_model(mapping, arch, template_model, asmbench):
    try:
        isa = MachineModel.get_isa_for_arch(arch)
    except:
        print("Skipping...", file=sys.stderr)
        return None
    if template_model == None:
        mm = MachineModel(isa=isa)
    else:
        mm = template_model
    parser = get_parser(isa)

    for port in mapping['arch']['ports']:
        mm.add_port(port)

    for insn in mapping['arch']['insns']:
        try:
            ports = mapping['assignment'][insn]

            # Parse instruction
            insn_split = insn.split('_')
            name = insn_split[1]
            insn_parts = list(('_' + '_'.join(insn_split[2:])).split(','))
            operands = []
            state = {}
            for op in insn_parts:
                parsed = operand_parse(op, state)
                if parsed != None:
                    operands.append(parsed)

            # Port pressures from mapping
            port_pressure = port_convert(ports)

            # Initial guessed throughput and latency
            throughput = throughput_guess(ports)
            latency = latency_guess(ports)

            # Benchmark with asmbench
            # print(build_bench_instruction(name, operands))
            if asmbench:
                bench_latency, bench_throughput = bench_instruction(name, operands)
                if bench_throughput != None:
                    throughput = round_cycles(bench_throughput)
                else:
                    print("Failed to measure throughput for instruction {}.".format(insn))
                if bench_latency != None:
                    latency = round_cycles(bench_latency)
                else:
                    print("Failed to measure latency for instruction {}.".format(insn))

            # No u-ops data available
            uops = None

            # Insert instruction if not already found (can happen with template)
            if mm.get_instruction(name, operands) == None:
                mm.set_instruction(name, operands, latency, port_pressure, throughput, uops)
        except ValueError as e:
            print("Failed to parse instruction {}: {}.".format(insn, e))

    return mm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json', help='path of mapping.json')
    parser.add_argument('yaml', help='path of template.yml', nargs='?')
    parser.add_argument('--asmbench', help='Benchmark latency and throughput using asmbench.',
                        action='store_true')
    args = parser.parse_args()
    basename = os.path.basename(__file__)

    json_file = open(args.json, 'r')
    mapping = json.load(json_file)
    arch = mapping['arch']['name'].lower()
    json_file.close()

    template_model = None
    if args.yaml != None:
        template_model = MachineModel(path_to_yaml=args.yaml)

    if args.asmbench:
        bench.setup_llvm()

    model = extract_model(mapping, arch, template_model, args.asmbench)

    with open('{}.yml'.format(arch.lower()), 'w') as f:
        f.write(model.dump())


if __name__ == '__main__':
    main()
