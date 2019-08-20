#!/usr/bin/env python3
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from distutils.version import StrictVersion
from itertools import groupby, product

from ruamel import yaml

from osaca.api import add_entries_to_db
from osaca.parser import ParserAArch64v81, ParserX86ATT
from osaca.semantics import MachineModel

ARCH_DICT = {
    'vulcan': 'aarch64',
    'snb': 'x86',
    'ivb': 'x86',
    'hsw': 'x86',
    'bdw': 'x86',
    'skl': 'x86',
    'skx': 'x86',
    'csx': 'x86',
}


def port_pressure_from_tag_attributes(attrib, arch, ports):
    # apply cycles for D ports
    data_port = re.compile(r'[0-9]D$')
    data_ports = [x[:-1] for x in filter(data_port.match, ports)]

    # format attributes
    cycles = attrib['ports'].split('+')
    cycles = [c.split('*') for c in cycles]
    for i, c in enumerate(cycles):
        cycles[i][0] = int(c[0])
        if str(c[1]).startswith('p'):
            cycles[i][1] = [p for p in c[1][1:]]
        if data_ports and data_ports == cycles[i][1]:
            # uops for data ports
            cycles.append([c[0], [x + 'D' for x in data_ports]])
        cycles[i][0] = [
            cycles[i][0] / num for num in range(1, len(cycles[i][1]) + 1) for _ in range(num)
        ]
    cycles = [list(product(c[0], c[1])) for c in cycles]
    all_options = []

    # iterate over all combinations of all uop options
    for cycles_combs in cycles:
        options = []
        tmp_opt = []
        total = cycles_combs[0][0]
        # iterate over all combinations of each uop option
        for comb in cycles_combs:
            # add options until they reach the total num of uops
            tmp_opt.append(comb)
            if sum([c[0] for c in tmp_opt]) == total:
                # copy this option as one of several to the cycle option list
                options.append(tmp_opt.copy())
                tmp_opt = []
        if len(tmp_opt) != 0:
            raise ValueError('Cannot compute port pressure')
        options = [x for x, _ in groupby(options)]
        all_options.append(options)
    all_options = list(product(*all_options))

    # find best scheduling
    port_pressure = {}
    for p in ports:
        port_pressure[p] = 0.0
    first = calculate_port_pressure(all_options[0])
    for key in first:
        port_pressure[key] = first[key]
    for option in all_options[1:]:
        tmp = calculate_port_pressure(option)
        if (max(list(tmp.values())) <= max(list(port_pressure.values()))) and (
            len(tmp) > len([x for x in port_pressure.values() if x != 0.0])
        ):
            for k in port_pressure:
                port_pressure[k] = tmp[k] if k in tmp else 0.0

    # check if calculation equals given throughput
    if abs(max(list(port_pressure.values())) - float(attrib['TP_ports'])) > 0.01:
        print('Contradicting TP value compared to port_pressure. Ignore port pressure.')
        for p in port_pressure:
            port_pressure[p] = 0.0
        return port_pressure

    # Also consider DIV pipeline
    if 'div_cycles' in attrib:
        div_port = re.compile(r'[0-9]DV$')
        div_ports = [x for x in filter(div_port.match, ports)]
        for dp in div_ports:
            port_pressure[dp] += int(attrib['div_cycles']) / len(div_ports)
    return port_pressure


def calculate_port_pressure(pp_option):
    ports = {}
    for option in pp_option:
        for port in option:
            if port[1] in ports:
                ports[port[1]] += port[0]
            else:
                ports[port[1]] = port[0]
    return ports


def extract_paramters(instruction_tag, arch):
    isa = ARCH_DICT[arch.lower()]
    parser = ParserX86ATT()
    if isa == 'aarch64':
        parser = ParserAArch64v81()
    elif isa == 'x86':
        parser = ParserX86ATT()
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
            parameter['base'] = 'gpr'
            parameter['offset'] = None
            parameter['index'] = None
            parameter['scale'] = 1
            parameters.append(parameter)
        elif p_type == 'reg':
            parameter['class'] = 'register'
            possible_regs = [
                parser.parse_register('%' + r) for r in parameter_tag.text.split(',')
            ]
            if possible_regs[0] is None:
                raise ValueError(
                    'Unknown register type for {} with {}.'.format(
                        parameter_tag.attrib, parameter_tag.text
                    )
                )
            if isa == 'x86':
                if parser.is_vector_register(possible_regs[0]['register']):
                    possible_regs[0]['register']['name'] = possible_regs[0]['register']['name'].lower()[:3]
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
            # FIXME actually only address generation
            parameter['class'] = 'memory'
            parameter['base'] = 'gpr'
            parameter['offset'] = None
            parameter['index'] = None
            parameter['scale'] = 1
            parameters.append(parameter)
            parameters.append(parameter)
        else:
            raise ValueError("Unknown paramter type {}".format(parameter_tag.attrib))
    return parameters


def extract_model(tree, arch):
    mm = MachineModel(arch.lower())
    ports = mm._data['ports']
    model_data = []
    for instruction_tag in tree.findall('.//instruction'):
        ignore = False

        mnemonic = instruction_tag.attrib['asm']

        # Extract parameter components
        try:
            parameters = extract_paramters(instruction_tag, arch)
            if ARCH_DICT[arch.lower()] == 'x86':
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
                port_pressure.append(
                    port_pressure_from_tag_attributes(measurement_tag.attrib, arch, ports)
                )
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
                print("Contradicting latencies found:", mnemonic, file=sys.stderr)
                ignore = True
            elif latencies:
                latency = latencies[0]

        # Ordered by IACA version (newest last)
        for iaca_tag in sorted(
            arch_tag.iter('IACA'), key=lambda i: StrictVersion(i.attrib['version'])
        ):
            if 'ports' in iaca_tag.attrib:
                port_pressure.append(
                    port_pressure_from_tag_attributes(iaca_tag.attrib, arch, ports)
                )
        if ignore:
            continue

        # Check if all are equal
        if port_pressure:
            if port_pressure[1:] != port_pressure[:-1]:
                print(
                    "Contradicting port occupancies, using latest IACA:", mnemonic, file=sys.stderr
                )
            port_pressure = port_pressure[-1]
            throughput = max(list(port_pressure.values()) + [0.0])
        else:
            # print("No data available for this architecture:", mnemonic, file=sys.stderr)
            continue
        # ---------------------------------------------
        model_data.append(
            {
                'name': mnemonic,
                'operands': parameters,
                'uops': uops,
                'throughput': throughput,
                'latency': latency,
                'port_pressure': port_pressure,
            }
        )

    return model_data


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

    tree = ET.parse(args.xml)
    if args.arch:
        model_data = extract_model(tree, args.arch)
        print(yaml.dump(model_data, allow_unicode=True))
    else:
        for arch in architectures(tree):
            model_data = extract_model(tree, arch)
            add_entries_to_db(arch, model_data)


if __name__ == '__main__':
    main()
