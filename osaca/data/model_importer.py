#!/usr/bin/env python3
import os.path
import argparse
import sys
import xml.etree.ElementTree as ET
from distutils.version import StrictVersion

from osaca.parser import get_parser
from osaca.semantics import MachineModel


def port_pressure_from_tag_attributes(attrib):
    # '1*p015+1*p1+1*p23+1*p4+3*p5' ->
    # [[1, '015'], [1, '1'], [1, '23'], [1, '4'], [3, '5']]
    port_occupation = []
    for p in attrib['ports'].split('+'):
        cycles, ports = p.split('*')
        ports = ports.lstrip('p')
        port_occupation.append([int(cycles), ports])

    # Also
    if 'div_cycles' in attrib:
        port_occupation.append([int(attrib['div_cycles']), ['DIV']])

    return port_occupation


def extract_paramters(instruction_tag, parser, isa):
    # Extract parameter components
    parameters = []  # used to store string representations
    parameter_tags = sorted(instruction_tag.findall("operand"), key=lambda p: int(p.attrib['idx']))
    for parameter_tag in parameter_tags:
        parameter = {}
        # Ignore parameters with suppressed=1
        if int(parameter_tag.attrib.get('suppressed', '0')):
            continue

        p_type = parameter_tag.attrib['type']
        if p_type == 'imm':
            parameter['class'] = 'immediate'
            parameter['imd'] = 'int'
            parameters.append(parameter)
        elif p_type == 'mem':
            parameter['class'] = 'memory'
            parameter['base'] = "*"
            parameter['offset'] = "*"
            parameter['index'] = "*"
            parameter['scale'] = "*"
            parameters.append(parameter)
        elif p_type == 'reg':
            parameter['class'] = 'register'
            possible_regs = [parser.parse_register('%' + r) for r in parameter_tag.text.split(',')]
            if possible_regs[0] is None:
                raise ValueError(
                    'Unknown register type for {} with {}.'.format(
                        parameter_tag.attrib, parameter_tag.text
                    )
                )
            if isa == 'x86':
                if parser.is_vector_register(possible_regs[0]['register']):
                    possible_regs[0]['register']['name'] = possible_regs[0]['register'][
                        'name'
                    ].lower()[:3]
                    if 'mask' in possible_regs[0]['register']:
                        possible_regs[0]['register']['mask'] = True
                else:
                    possible_regs[0]['register']['name'] = 'gpr'
            elif isa == 'aarch64':
                del possible_regs['register']['name']
            for key in possible_regs[0]['register']:
                parameter[key] = possible_regs[0]['register'][key]
            parameters.append(parameter)
        elif p_type == 'relbr':
            parameter['class'] = 'identifier'
            parameters.append(parameter)
        elif p_type == 'agen':
            parameter['class'] = 'memory'
            parameter['base'] = "*"
            parameter['offset'] = "*"
            parameter['index'] = "*"
            parameter['scale'] = "*"
            parameters.append(parameter)
        else:
            raise ValueError("Unknown paramter type {}".format(parameter_tag.attrib))
    return parameters


def extract_model(tree, arch):
    try:
        isa = MachineModel.get_isa_for_arch(arch)
    except:
        print("Skipping...", file=sys.stderr)
        return None
    mm = MachineModel(isa=isa)
    parser = get_parser(isa)

    for instruction_tag in tree.findall('.//instruction'):
        ignore = False

        mnemonic = instruction_tag.attrib['asm']
        # skip any mnemonic which contain spaces (e.g., "REX CRC32")
        if ' ' in mnemonic:
            continue

        # Extract parameter components
        try:
            parameters = extract_paramters(instruction_tag, parser, isa)
            if isa == 'x86':
                parameters.reverse()
        except ValueError as e:
            print(e, file=sys.stderr)

        # Extract port occupation, throughput and latency
        port_pressure, throughput, latency, uops = [], None, None, None
        arch_tag = instruction_tag.find('architecture[@name="' + arch.upper() + '"]')
        if arch_tag is None:
            continue
        # We collect all measurement and IACA information and compare them later
        for measurement_tag in arch_tag.iter('measurement'):
            if 'TP_ports' in measurement_tag.attrib:
                throughput = measurement_tag.attrib['TP_ports']
            else:
                throughput = (
                    measurement_tag.attrib['TP'] if 'TP' in measurement_tag.attrib else None
                )
            uops = (
                int(measurement_tag.attrib['uops']) if 'uops' in measurement_tag.attrib else None
            )
            if 'ports' in measurement_tag.attrib:
                port_pressure.append(port_pressure_from_tag_attributes(measurement_tag.attrib))
            latencies = [
                int(l_tag.attrib['cycles'])
                for l_tag in measurement_tag.iter('latency')
                if 'cycles' in l_tag.attrib
            ]
            if len(latencies) == 0:
                latencies = [
                    int(l_tag.attrib['max_cycles'])
                    for l_tag in measurement_tag.iter('latency')
                    if 'max_cycles' in l_tag.attrib
                ]
            if latencies[1:] != latencies[:-1]:
                print("Contradicting latencies found, using first:", mnemonic, latencies,
                      file=sys.stderr)
            if latencies:
                latency = latencies[0]
        if ignore:
            continue

        # Ordered by IACA version (newest last)
        for iaca_tag in sorted(
            arch_tag.iter('IACA'), key=lambda i: StrictVersion(i.attrib['version'])
        ):
            if 'ports' in iaca_tag.attrib:
                port_pressure.append(port_pressure_from_tag_attributes(iaca_tag.attrib))

        # Check if all are equal
        if port_pressure:
            if port_pressure[1:] != port_pressure[:-1]:
                print(
                    "Contradicting port occupancies, using latest IACA:",
                    mnemonic, file=sys.stderr)
            port_pressure = port_pressure[-1]

            # Add missing ports:
            for ports in [pp[1] for pp in port_pressure]:
                for p in ports:
                    mm.add_port(p)

            throughput = max(mm.average_port_pressure(port_pressure))
        else:
            # print("No data available for this architecture:", mnemonic, file=sys.stderr)
            continue
        # ---------------------------------------------
        mm.set_instruction(mnemonic, parameters, latency, port_pressure, throughput, uops)

    return mm


def rhs_comment(uncommented_string, comment):
    max_length = max([len(l) for l in uncommented_string.split('\n')])

    commented_string = ""
    for l in uncommented_string.split('\n'):
        commented_string += ("{:<"+str(max_length)+"}  # {}\n").format(l, comment)
    return commented_string


def architectures(tree):
    return set([a.attrib['name'] for a in tree.findall('.//architecture')])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('xml', help='path of instructions.xml from http://uops.info')
    parser.add_argument(
        'arch',
        nargs='?',
        help='architecture to extract, use IACA abbreviations (e.g., SNB). '
        'if not given, all will be extracted and saved to file in CWD.',
    )
    args = parser.parse_args()
    basename = os.path.basename(__file__)

    tree = ET.parse(args.xml)
    print('Available architectures:', ', '.join(architectures(tree)))
    if args.arch:
        model = extract_model(tree, args.arch)
        if model is not None:
            print(rhs_comment(model.dump(), basename+" "+sys.argv[0]))
    else:
        for arch in architectures(tree):
            print(arch, end='')
            model = extract_model(tree, arch.lower())
            model_string = rhs_comment(model.dump(), basename+" "+arch)
            
            with open('{}.yml'.format(arch.lower()), 'w') as f:
                f.write(model_string)
            print('.')


if __name__ == '__main__':
    main()
