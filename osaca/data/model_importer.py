#!/usr/bin/env python3
from collections import defaultdict, OrderedDict
import xml.etree.ElementTree as ET
import re
import sys
import argparse
from distutils.version import StrictVersion

from osaca.param import Parameter, Register


def normalize_reg_name(reg_name):
    # strip spaces
    reg_name = reg_name.strip()
    # masks are denoted with curly brackets in uops.info
    reg_name = re.sub(r'{K([0-7])}', r'K\1', reg_name)
    reg_name = re.sub(r'ST\(([0-7])\)', r'ST\1', reg_name)
    return reg_name


def port_occupancy_from_tag_attributes(attrib):
    occupancy = defaultdict(int)
    for k, v in attrib.items():
        if not k.startswith('port'):
            continue
        potential_ports = list(k[4:])
        per_port_occupancy = int(v) / len(potential_ports)
        for pp in potential_ports:
            occupancy[pp] += per_port_occupancy
    return dict(occupancy)


def extract_model(tree, arch):
    model_data = []
    for instruction_tag in tree.findall('//instruction'):
        ignore = False

        mnemonic = instruction_tag.attrib['asm']

        # Extract parameter components
        parameters = []  # used to store string representations
        parameter_tags = sorted(instruction_tag.findall("operand"),
                                 key=lambda p: int(p.attrib['idx']))
        for parameter_tag in parameter_tags:
            # Ignore parameters with suppressed=1
            if int(parameter_tag.attrib.get('suppressed', '0')):
                continue

            p_type = parameter_tag.attrib['type']
            if p_type == 'imm':
                parameters.append('imd')  # Parameter('IMD')
            elif p_type == 'mem':
                parameters.append('mem')  # Parameter('MEM')
            elif p_type == 'reg':
                possible_regs = [normalize_reg_name(r)
                                 for r in parameter_tag.text.split(',')]
                reg_groups = [Register.sizes.get(r, None) for r in possible_regs]
                if reg_groups[1:] == reg_groups[:-1]:
                    if reg_groups[0] is None:
                        print('Unknown register type for', mnemonic, ':',
                              parameter_tag.attrib, parameter_tag.text,
                              file=sys.stderr)
                        ignore = True
                    elif reg_groups[0][1] == 'GPR':
                        parameters.append('r{}'.format(reg_groups[0][0]))  # Register(possible_regs[0]))
                    elif '{' in parameter_tag.text:
                        # We have a mask
                        parameters[-1] += '{opmask}'
                    else:
                        parameters.append(reg_groups[0][1].lower())
            elif p_type == 'relbr':
                parameters.append('LBL')
            elif p_type == 'agen':
                parameters.append('mem')
            else:
                print("Unknown paramter type:", parameter_tag.attrib, file=sys.stderr)
                ignore = True
        if ignore: continue

        # Extract port occupation, throughput and latency
        port_occupancy, throughput, latency = [], 0.0, None
        arch_tag = instruction_tag.find('architecture[@name="'+arch+'"]')
        if arch_tag is None:
            continue
        # We collect all measurement and IACA information and compare them later
        for measurement_tag in arch_tag.iter('measurement'):
            port_occupancy.append(port_occupancy_from_tag_attributes(measurement_tag.attrib))
            # FIXME handle min/max Latencies ('maxCycles' and 'minCycles')
            latencies = [int(l_tag.attrib['cycles'])
                         for l_tag in measurement_tag.iter('latency') if 'latency' in l_tag.attrib]

            if latencies[1:] != latencies[:-1]:
                print("Contradicting latencies found:", mnemonic, file=sys.stderr)
                ignore = True
            elif latencies:
                latency = latencies[0]
        # Ordered by IACA version (newest last)
        for iaca_tag in sorted(arch_tag.iter('IACA'),
                               key=lambda i: StrictVersion(i.attrib['version'])):
            port_occupancy.append(port_occupancy_from_tag_attributes(iaca_tag.attrib))
        if ignore: continue

        # Check if all are equal
        if port_occupancy:
            if port_occupancy[1:] != port_occupancy[:-1]:
                print("Contradicting port occupancies, using latest IACA:", mnemonic,
                      file=sys.stderr)
            port_occupancy = port_occupancy[-1]
            throughput = max(list(port_occupancy.values())+[0.0])
        else:
            # print("No data available for this architecture:", mnemonic, file=sys.stderr)
            continue

        for m, p in build_variants(mnemonic, parameters):
            model_data.append((m.lower() + '-' + '_'.join(p),
                              throughput, latency, port_occupancy))

    return model_data


def all_or_false(iter):
    if not iter:
        return False
    else:
        return all(iter)


def build_variants(mnemonic, parameters):
    """Yield all resonable variants of this instruction form."""
    # The one that was given
    mnemonic = mnemonic.upper()
    yield mnemonic, parameters

    # Without opmask
    if any(['{opmask}' in p for p in parameters]):
        yield mnemonic, list([p.replace('{opmask}', '') for p in parameters])

    # With suffix (assuming suffix was not already present)
    suffixes = {'Q': 'r64',
                'L': 'r32',
                'W': 'r16',
                'B': 'r8'}
    for s, reg in suffixes.items():
        if not mnemonic.endswith(s) and all_or_false(
                [p == reg for p in parameters if p not in ['mem', 'imd']]):
            yield mnemonic+s, parameters


def architectures(tree):
    return set([a.attrib['name'] for a in tree.findall('.//architecture')])


def dump_csv(model_data):
    csv = 'instr,TP,LT,ports\n'
    ports = set()
    for mnemonic, throughput, latency, port_occupancy in model_data:
        for p in port_occupancy:
            ports.add(p)

    for mnemonic, throughput, latency, port_occupancy in model_data:
        for p in ports:
            if p not in port_occupancy:
                port_occupancy[p] = 0.0
        po_items = sorted(port_occupancy.items())
        csv_line = '{},{},{},"({})"\n'.format(mnemonic, throughput, latency,
                                              ','.join([str(c) for p, c in po_items]))
        csv += csv_line
    return csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('xml', help='path of instructions.xml from http://uops.info')
    parser.add_argument('arch', nargs='?',
                        help='architecture to extract, use IACA abbreviations (e.g., SNB). '
                             'if not given, all will be extracted and saved to file in CWD.')
    args = parser.parse_args()

    tree = ET.parse(args.xml)
    if args.arch:
        model_data = extract_model(tree, args.arch)
        print(dump_csv(model_data))
    else:
        for arch in architectures(tree):
            model_data = extract_model(tree, arch)
            with open('{}_data.csv'.format(arch), 'w') as f:
                f.write(dump_csv(model_data))


if __name__ == '__main__':
    main()
