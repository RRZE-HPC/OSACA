#!/usr/bin/env python3
from collections import defaultdict
from fractions import Fraction


class EntryBuilder:
    @staticmethod
    def compute_throughput(port_pressure):
        port_occupancy = defaultdict(Fraction)
        for uops, ports in port_pressure:
            for p in ports:
                port_occupancy[p] += Fraction(uops, len(ports))
        return float(max(list(port_occupancy.values()) + [0]))

    @staticmethod
    def classify(operands_types):
        load = "mem" in operands_types[:-1]
        store = "mem" in operands_types[-1:]
        assert not (load and store), "Can not process a combined load-store instruction."
        return load, store

    def build_description(
        self, instruction_name, operand_types, port_pressure=[], latency=0, comment=None
    ):
        if comment:
            comment = "  # " + comment
        else:
            comment = ""
        description = "- name: {}{}\n  operands:\n".format(instruction_name, comment)

        for ot in operand_types:
            if ot == "imd":
                description += "  - class: immediate\n    imd: int\n"
            elif ot.startswith("mem"):
                description += "  - class: memory\n" '    base: "*"\n' '    offset: "*"\n'
                if ot == "mem_simple":
                    description += "    index: ~\n"
                elif ot == "mem_complex":
                    description += "    index: gpr\n"
                else:
                    description += '    index: "*"\n'
                description += '    scale: "*"\n'
            else:
                if "{k}" in ot:
                    description += "  - class: register\n    name: {}\n    mask: True\n".format(
                        ot.replace("{k}", "")
                    )
                else:
                    description += "  - class: register\n    name: {}\n".format(ot)

        description += (
            "  latency: {latency}\n"
            "  port_pressure: {port_pressure!r}\n"
            "  throughput: {throughput}\n"
            "  uops: {uops}\n"
        ).format(
            latency=latency,
            port_pressure=port_pressure,
            throughput=self.compute_throughput(port_pressure),
            uops=sum([i for i, p in port_pressure]),
        )
        return description

    def parse_port_pressure(self, port_pressure_str):
        """
        Example:
        1*p45+2*p0 -> [[1, '45'], [2, '0']]
        """
        port_pressure = []
        if port_pressure_str:
            for p in port_pressure_str.split("+"):
                cycles, ports = p.split("*p")
                if ports.startswith("(") and ports.endswith(")"):
                    ports = ports[1:-1].split(",")
                port_pressure.append([int(cycles), ports])
        return port_pressure

    def process_item(self, instruction_form, resources):
        """
        Example:
        ('mov xmm mem', ('1*p45+2*p0', 7) -> ('mov', ['xmm', 'mem'], [[1, '45'], [2, '0']], 7)
        """
        if instruction_form.startswith("[") and "]" in instruction_form:
            instr_elements = instruction_form.split("]")
            instr_elements = [instr_elements[0] + "]"] + instr_elements[1].strip().split(" ")
        else:
            instr_elements = instruction_form.split(" ")
        latency = int(resources[1])
        port_pressure = self.parse_port_pressure(resources[0])
        instruction_name = instr_elements[0]
        operand_types = instr_elements[1:]
        return self.build_description(instruction_name, operand_types, port_pressure, latency)


class EntryBuilderIntelPort9(EntryBuilder):
    # for ICX

    def build_description(self, instruction_name, operand_types, port_pressure=[], latency=0):
        load, store = self.classify(operand_types)

        if load:
            port_pressure += [[1, "23"], [1, ["2D", "3D"]]]
            latency += 5
            comment = "with load"
            return EntryBuilder.build_description(
                self, instruction_name, operand_types, port_pressure, latency, comment
            )
        if store:
            port_pressure = port_pressure + [[1, "79"], [1, "48"]]
            operands = ["mem" if o == "mem" else o for o in operand_types]
            latency += 0
            return EntryBuilder.build_description(
                self,
                instruction_name,
                operands,
                port_pressure,
                latency,
                "with store",
            )

        # Register only:
        return EntryBuilder.build_description(
            self, instruction_name, operand_types, port_pressure, latency
        )


def get_description(instruction_form, port_pressure, latency, rhs_comment=None):
    entry = EntryBuilderIntelPort9().process_item(instruction_form, (port_pressure, latency))

    if rhs_comment is not None:
        max_length = max([len(line) for line in entry.split("\n")])

        commented_entry = ""
        for line in entry.split("\n"):
            commented_entry += ("{:<" + str(max_length) + "}  # {}\n").format(line, rhs_comment)
        entry = commented_entry

    return entry


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("Usage: {} <INSTRUCTION> <PORT_PRESSURE> <LATENCY> [COMMENT]".format(sys.argv[0]))
        sys.exit(0)

    try:
        print(get_description(*sys.argv[1:]))
    except KeyError:
        print("Unknown architecture.")
        sys.exit(1)