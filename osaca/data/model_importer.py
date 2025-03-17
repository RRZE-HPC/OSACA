#!/usr/bin/env python3
import argparse
import os.path
import sys
import xml.etree.ElementTree as ET
from distutils.version import StrictVersion

from osaca.parser import get_parser
from osaca.semantics import MachineModel

intel_archs = [
    "CON",
    "WOL",
    "NHM",
    "WSM",
    "SNB",
    "IVB",
    "HSW",
    "BDW",
    "SKL",
    "SKX",
    "KBL",
    "CFL",
    "CNL",
    "ICL",
]
amd_archs = ["ZEN1", "ZEN+", "ZEN2"]


def port_pressure_from_tag_attributes(attrib):
    # '1*p015+1*p1+1*p23+1*p4+3*p5' ->
    # [[1, '015'], [1, '1'], [1, '23'], [1, '4'], [3, '5']]
    port_occupation = []
    for p in attrib["ports"].split("+"):
        cycles, ports = p.split("*")
        ports = ports.lstrip("p")
        ports = ports.lstrip("FP")
        port_occupation.append([int(cycles), ports])

    # Also consider div on DIV pipeline
    if "div_cycles" in attrib:
        port_occupation.append([int(attrib["div_cycles"]), ["DIV"]])

    return port_occupation


def extract_paramters(instruction_tag, parser, isa):
    # Extract parameter components
    parameters = []  # used to store string representations
    parameter_tags = sorted(instruction_tag.findall("operand"), key=lambda p: int(p.attrib["idx"]))
    for parameter_tag in parameter_tags:
        parameter = {}
        # Ignore parameters with suppressed=1
        if int(parameter_tag.attrib.get("suppressed", "0")):
            continue

        p_type = parameter_tag.attrib["type"]
        if p_type == "imm":
            parameter["class"] = "immediate"
            parameter["imd"] = "int"
            parameters.append(parameter)
        elif p_type == "mem":
            parameter["class"] = "memory"
            parameter["base"] = "*"
            parameter["offset"] = "*"
            parameter["index"] = "*"
            parameter["scale"] = "*"
            parameters.append(parameter)
        elif p_type == "reg":
            parameter["class"] = "register"
            possible_regs = [parser.parse_register("%" + r) for r in parameter_tag.text.split(",")]
            if possible_regs[0] is None:
                raise ValueError(
                    "Unknown register type for {} with {}.".format(
                        parameter_tag.attrib, parameter_tag.text
                    )
                )
            if isa == "x86":
                if parser.is_vector_register(possible_regs[0]["register"]):
                    possible_regs[0]["register"]["name"] = possible_regs[0]["register"][
                        "name"
                    ].lower()[:3]
                    if "mask" in possible_regs[0]["register"]:
                        possible_regs[0]["register"]["mask"] = True
                else:
                    possible_regs[0]["register"]["name"] = "gpr"
            elif isa == "aarch64":
                del possible_regs["register"]["name"]
            for key in possible_regs[0]["register"]:
                parameter[key] = possible_regs[0]["register"][key]
            parameters.append(parameter)
        elif p_type == "relbr":
            parameter["class"] = "identifier"
            parameters.append(parameter)
        elif p_type == "agen":
            parameter["class"] = "memory"
            parameter["base"] = "*"
            parameter["offset"] = "*"
            parameter["index"] = "*"
            parameter["scale"] = "*"
            parameters.append(parameter)
        else:
            raise ValueError("Unknown paramter type {}".format(parameter_tag.attrib))
    return parameters


def extract_model(tree, arch, skip_mem=True):
    try:
        isa = MachineModel.get_isa_for_arch(arch)
    except Exception:
        print("Skipping...", file=sys.stderr)
        return None
    mm = MachineModel(isa=isa)
    # The model uses the AT&T syntax.
    parser = get_parser(isa, "ATT")

    for instruction_tag in tree.findall(".//instruction"):
        ignore = False

        mnemonic = instruction_tag.attrib["asm"]
        iform = instruction_tag.attrib["iform"]
        # reduce to second part if mnemonic contain space (e.g., "REX CRC32")
        if " " in mnemonic:
            mnemonic = mnemonic.split(" ", 1)[1]

        # Extract parameter components
        try:
            parameters = extract_paramters(instruction_tag, parser, isa)
            if isa == "x86":
                parameters.reverse()
        except ValueError as e:
            print(e, file=sys.stderr)

        # Extract port occupation, throughput and latency
        port_pressure, throughput, latency, uops = [], None, None, None
        arch_tag = instruction_tag.find('architecture[@name="' + arch.upper() + '"]')
        if arch_tag is None:
            continue
        # skip any instructions without port utilization
        if not any(["ports" in x.attrib for x in arch_tag.findall("measurement")]):
            print("Couldn't find port utilization, skip: ", iform, file=sys.stderr)
            continue
        # skip if measured TP is smaller than computed
        if [
            float(x.attrib["TP_ports"])
            > min(float(x.attrib["TP_loop"]), float(x.attrib["TP_unrolled"]))
            for x in arch_tag.findall("measurement")
        ][0]:
            print(
                "Calculated TP is greater than measured TP.",
                iform,
                file=sys.stderr,
            )
        # skip if instruction contains memory operand
        if skip_mem and any(
            [x.attrib["type"] == "mem" for x in instruction_tag.findall("operand")]
        ):
            print("Contains memory operand, skip: ", iform, file=sys.stderr)
            continue
        # We collect all measurement and IACA information and compare them later
        for measurement_tag in arch_tag.iter("measurement"):
            if "TP_ports" in measurement_tag.attrib:
                throughput = float(measurement_tag.attrib["TP_ports"])
            else:
                throughput = min(
                    measurement_tag.attrib.get("TP_loop", float("inf")),
                    measurement_tag.attrib.get("TP_unroll", float("inf")),
                    measurement_tag.attrib.get("TP", float("inf")),
                )
                if throughput == float("inf"):
                    throughput = None
            uops = (
                int(measurement_tag.attrib["uops"]) if "uops" in measurement_tag.attrib else None
            )
            if "ports" in measurement_tag.attrib:
                port_pressure.append(port_pressure_from_tag_attributes(measurement_tag.attrib))
            latencies = [
                int(l_tag.attrib["cycles"])
                for l_tag in measurement_tag.iter("latency")
                if "cycles" in l_tag.attrib
            ]
            if len(latencies) == 0:
                latencies = [
                    int(l_tag.attrib["max_cycles"])
                    for l_tag in measurement_tag.iter("latency")
                    if "max_cycles" in l_tag.attrib
                ]
            if latencies[1:] != latencies[:-1]:
                print(
                    "Contradicting latencies found, using smallest:",
                    iform,
                    latencies,
                    file=sys.stderr,
                )
            if latencies:
                latency = min(latencies)
        if ignore:
            continue

        # Ordered by IACA version (newest last)
        for iaca_tag in sorted(
            arch_tag.iter("IACA"), key=lambda i: StrictVersion(i.attrib["version"])
        ):
            if "ports" in iaca_tag.attrib:
                port_pressure.append(port_pressure_from_tag_attributes(iaca_tag.attrib))

        # Check if all are equal
        if port_pressure:
            if port_pressure[1:] != port_pressure[:-1]:
                print(
                    "Contradicting port occupancies, using latest IACA:",
                    iform,
                    file=sys.stderr,
                )
            port_pressure = port_pressure[-1]
        else:
            # print("No data available for this architecture:", mnemonic, file=sys.stderr)
            continue

        # Adding Intel's 2D and 3D pipelines on Intel µarchs, without Ice Lake:
        if arch.upper() in intel_archs and not arch.upper() in ["ICL"]:
            if any([p["class"] == "memory" for p in parameters]):
                # We have a memory parameter, if ports 2 & 3 are present, also add 2D & 3D
                # TODO remove port7 on 'hsw' onward and split entries depending on addressing mode
                port_23 = False
                port_4 = False
                for i, pp in enumerate(port_pressure):
                    if "2" in pp[1] and "3" in pp[1]:
                        port_23 = True
                    if "4" in pp[1]:
                        port_4 = True
                # Add (x, ['2D', '3D']) if load ports (2 & 3) are used, but not the store port (4)
                if port_23 and not port_4:
                    if (
                        arch.upper() in ["SNB", "IVB"]
                        and any([p.get("name", "") == "ymm" for p in parameters])
                        and not ("128" in mnemonic)
                    ):
                        # x = 2 if SNB or IVB and ymm regiser in any operand and not '128' in
                        # instruction name
                        port2D3D_pressure = 2
                    else:
                        # otherwiese x = 1
                        port2D3D_pressure = 1
                    port_pressure.append((port2D3D_pressure, ["2D", "3D"]))

        # Add missing ports:
        for ports in [pp[1] for pp in port_pressure]:
            for p in ports:
                mm.add_port(p)

        throughput = max(mm.average_port_pressure(port_pressure))
        mm.set_instruction(mnemonic, parameters, latency, port_pressure, throughput, uops)
    # TODO eliminate entries which could be covered by automatic load / store expansion
    return mm


def rhs_comment(uncommented_string, comment):
    max_length = max([len(line) for line in uncommented_string.split("\n")])

    commented_string = ""
    for line in uncommented_string.split("\n"):
        commented_string += ("{:<" + str(max_length) + "}  # {}\n").format(line, comment)
    return commented_string


def architectures(tree):
    return set([a.attrib["name"] for a in tree.findall(".//architecture")])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", help="path of instructions.xml from http://uops.info")
    parser.add_argument(
        "arch",
        nargs="?",
        help="architecture to extract, use IACA abbreviations (e.g., SNB). "
        "if not given, all will be extracted and saved to file in CWD.",
    )
    parser.add_argument(
        "--mem",
        dest="skip_mem",
        action="store_false",
        help="add instruction forms including memory addressing operands, which are "
        "skipped by default",
    )
    args = parser.parse_args()
    basename = os.path.basename(__file__)

    tree = ET.parse(args.xml)
    print("# Available architectures:", ", ".join(architectures(tree)))
    if args.arch:
        print("# Chosen architecture: {}".format(args.arch))
        model = extract_model(tree, args.arch, args.skip_mem)
        if model is not None:
            print(rhs_comment(model.dump(), "uops.info import"))
    else:
        for arch in architectures(tree):
            print(arch, end="")
            model = extract_model(tree, arch.lower(), args.skip_mem)
            if model:
                model_string = rhs_comment(model.dump(), basename + " " + arch)

                with open("{}.yml".format(arch.lower()), "w") as f:
                    f.write(model_string)
                print(".")


if __name__ == "__main__":
    main()
