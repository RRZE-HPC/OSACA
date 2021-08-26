#!/usr/bin/env python3
from collections import OrderedDict, defaultdict
from fractions import Fraction


class MOVEntryBuilder:
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
                port_pressure.append([int(cycles), ports])
        return port_pressure

    def process_item(self, instruction_form, resources):
        """
        Example:
        ('mov xmm mem', ('1*p45+2*p0', 7) -> ('mov', ['xmm', 'mem'], [[1, '45'], [2, '0']], 7)
        """
        instr_elements = instruction_form.split(" ")
        latency = resources[1]
        port_pressure = self.parse_port_pressure(resources[0])
        instruction_name = instr_elements[0]
        operand_types = instr_elements[1:]
        return self.build_description(instruction_name, operand_types, port_pressure, latency)


class MOVEntryBuilderIntelNoPort7AGU(MOVEntryBuilder):
    # for SNB and IVB
    def build_description(self, instruction_name, operand_types, port_pressure=[], latency=0):
        load, store = self.classify(operand_types)

        comment = None
        if load:
            if "ymm" in operand_types:
                port2D3D_pressure = 2
            else:
                port2D3D_pressure = 1
            port_pressure += [[1, "23"], [port2D3D_pressure, ["2D", "3D"]]]
            latency += 4
            comment = "with load"
        if store:
            if "ymm" in operand_types:
                port4_pressure = 2
            else:
                port4_pressure = 1
            port_pressure += [[1, "23"], [port4_pressure, "4"]]
            latency += 0
            comment = "with store"

        return MOVEntryBuilder.build_description(
            self, instruction_name, operand_types, port_pressure, latency, comment
        )


class MOVEntryBuilderIntelWithPort7AGU(MOVEntryBuilder):
    # for HSW, BDW, SKX and CSX

    def build_description(self, instruction_name, operand_types, port_pressure=[], latency=0):
        load, store = self.classify(operand_types)

        if load:
            port_pressure += [[1, "23"], [1, ["2D", "3D"]]]
            latency += 4
            comment = "with load"
            return MOVEntryBuilder.build_description(
                self, instruction_name, operand_types, port_pressure, latency, comment
            )
        if store:
            port_pressure_simple = port_pressure + [[1, "237"], [1, "4"]]
            operands_simple = ["mem_simple" if o == "mem" else o for o in operand_types]
            port_pressure_complex = port_pressure + [[1, "23"], [1, "4"]]
            operands_complex = ["mem_complex" if o == "mem" else o for o in operand_types]
            latency += 0
            return (
                MOVEntryBuilder.build_description(
                    self,
                    instruction_name,
                    operands_simple,
                    port_pressure_simple,
                    latency,
                    "with store, simple AGU",
                )
                + "\n"
                + MOVEntryBuilder.build_description(
                    self,
                    instruction_name,
                    operands_complex,
                    port_pressure_complex,
                    latency,
                    "with store, complex AGU",
                )
            )

        # Register only:
        return MOVEntryBuilder.build_description(
            self, instruction_name, operand_types, port_pressure, latency
        )


np7 = MOVEntryBuilderIntelNoPort7AGU()
p7 = MOVEntryBuilderIntelWithPort7AGU()

# SNB
snb_mov_instructions = [
    # https://www.felixcloutier.com/x86/mov
    ("mov gpr gpr", ("1*p015", 1)),
    ("mov gpr mem", ("", 0)),
    ("mov mem gpr", ("", 0)),
    ("mov imd gpr", ("1*p015", 1)),
    ("mov imd mem", ("", 0)),
    ("movabs imd gpr", ("1*p015", 1)),  # AT&T version
    # https://www.felixcloutier.com/x86/movapd
    ("movapd xmm xmm", ("1*p5", 1)),
    ("movapd xmm mem", ("", 0)),
    ("movapd mem xmm", ("", 0)),
    ("vmovapd xmm xmm", ("1*p5", 1)),
    ("vmovapd xmm mem", ("", 0)),
    ("vmovapd mem xmm", ("", 0)),
    ("vmovapd ymm ymm", ("1*p5", 1)),
    ("vmovapd ymm mem", ("", 0)),
    ("vmovapd mem ymm", ("", 0)),
    # https://www.felixcloutier.com/x86/movaps
    ("movaps xmm xmm", ("1*p5", 1)),
    ("movaps xmm mem", ("", 0)),
    ("movaps mem xmm", ("", 0)),
    ("vmovaps xmm xmm", ("1*p5", 1)),
    ("movaps xmm mem", ("", 0)),
    ("movaps mem xmm", ("", 0)),
    ("vmovaps ymm ymm", ("1*p5", 1)),
    ("movaps ymm mem", ("", 0)),
    ("movaps mem ymm", ("", 0)),
    # https://www.felixcloutier.com/x86/movd:movq
    ("movd gpr mm", ("1*p5", 1)),
    ("movd mem mm", ("", 0)),
    ("movq gpr mm", ("1*p5", 1)),
    ("movq mem mm", ("", 0)),
    ("movd mm gpr", ("1*p0", 1)),
    ("movd mm mem", ("", 0)),
    ("movq mm gpr", ("1*p0", 1)),
    ("movq mm mem", ("", 0)),
    ("movd gpr xmm", ("1*p5", 1)),
    ("movd mem xmm", ("", 0)),
    ("movq gpr xmm", ("1*p5", 1)),
    ("movq mem xmm", ("", 0)),
    ("movd xmm gpr", ("1*p0", 1)),
    ("movd xmm mem", ("", 0)),
    ("movq xmm gpr", ("1*p0", 1)),
    ("movq xmm mem", ("", 0)),
    ("vmovd gpr xmm", ("1*p5", 1)),
    ("vmovd mem xmm", ("", 0)),
    ("vmovq gpr xmm", ("1*p5", 1)),
    ("vmovq mem xmm", ("", 0)),
    ("vmovd xmm gpr", ("1*p0", 1)),
    ("vmovd xmm mem", ("", 0)),
    ("vmovq xmm gpr", ("1*p0", 1)),
    ("vmovq xmm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movddup
    ("movddup xmm xmm", ("1*p5", 1)),
    ("movddup mem xmm", ("", 0)),
    ("vmovddup xmm xmm", ("1*p5", 1)),
    ("vmovddup mem xmm", ("", 0)),
    ("vmovddup ymm ymm", ("1*p5", 1)),
    ("vmovddup mem ymm", ("", 0)),
    # https://www.felixcloutier.com/x86/movdq2q
    ("movdq2q xmm mm", ("1*p015+1*p5", 1)),
    # https://www.felixcloutier.com/x86/movdqa:vmovdqa32:vmovdqa64
    ("movdqa xmm xmm", ("1*p015", 1)),
    ("movdqa mem xmm", ("", 0)),
    ("movdqa xmm mem", ("", 0)),
    ("vmovdqa xmm xmm", ("1*p015", 1)),
    ("vmovdqa mem xmm", ("", 0)),
    ("vmovdqa xmm mem", ("", 0)),
    ("vmovdqa ymm ymm", ("1*p05", 1)),
    ("vmovdqa mem ymm", ("", 0)),
    ("vmovdqa ymm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movdqu:vmovdqu8:vmovdqu16:vmovdqu32:vmovdqu64
    ("movdqu xmm xmm", ("1*p015", 1)),
    ("movdqu mem xmm", ("", 0)),
    ("movdqu xmm mem", ("", 0)),
    ("vmovdqu xmm xmm", ("1*p015", 1)),
    ("vmovdqu mem xmm", ("", 0)),
    ("vmovdqu xmm mem", ("", 0)),
    ("vmovdqu ymm ymm", ("1*p05", 1)),
    ("vmovdqu mem ymm", ("", 0)),
    ("vmovdqu ymm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movhlps
    ("movhlps xmm xmm", ("1*p5", 1)),
    ("vmovhlps xmm xmm xmm", ("1*p5", 1)),
    # https://www.felixcloutier.com/x86/movhpd
    ("movhpd mem xmm", ("1*p5", 1)),
    ("vmovhpd mem xmm xmm", ("1*p5", 1)),
    ("movhpd xmm mem", ("", 0)),
    ("vmovhpd mem xmm", ("", 0)),
    # https://www.felixcloutier.com/x86/movhps
    ("movhps mem xmm", ("1*p5", 1)),
    ("vmovhps mem xmm xmm", ("1*p5", 1)),
    ("movhps xmm mem", ("", 0)),
    ("vmovhps mem xmm", ("", 0)),
    # https://www.felixcloutier.com/x86/movlhps
    ("movlhps xmm xmm", ("1*p5", 1)),
    ("vmovlhps xmm xmm xmm", ("1*p5", 1)),
    # https://www.felixcloutier.com/x86/movlpd
    ("movlpd mem xmm", ("1*p5", 1)),
    ("vmovlpd mem xmm xmm", ("1*p5", 1)),
    ("movlpd xmm mem", ("", 0)),
    ("vmovlpd mem xmm", ("1*p5", 1)),
    # https://www.felixcloutier.com/x86/movlps
    ("movlps mem xmm", ("1*p5", 1)),
    ("vmovlps mem xmm xmm", ("1*p5", 1)),
    ("movlps xmm mem", ("", 0)),
    ("vmovlps mem xmm", ("1*p5", 1)),
    # https://www.felixcloutier.com/x86/movmskpd
    ("movmskpd xmm gpr", ("1*p0", 2)),
    ("vmovmskpd xmm gpr", ("1*p0", 2)),
    ("vmovmskpd ymm gpr", ("1*p0", 2)),
    # https://www.felixcloutier.com/x86/movmskps
    ("movmskps xmm gpr", ("1*p0", 1)),
    ("vmovmskps xmm gpr", ("1*p0", 1)),
    ("vmovmskps ymm gpr", ("1*p0", 1)),
    # https://www.felixcloutier.com/x86/movntdq
    ("movntdq xmm mem", ("", 0)),  # TODO NT-store: what latency to use?
    ("vmovntdq xmm mem", ("", 0)),  # TODO NT-store: what latency to use?
    ("vmovntdq ymm mem", ("", 0)),  # TODO NT-store: what latency to use?
    # https://www.felixcloutier.com/x86/movntdqa
    ("movntdqa mem xmm", ("", 0)),
    ("vmovntdqa mem xmm", ("", 0)),
    ("vmovntdqa mem ymm", ("", 0)),
    # https://www.felixcloutier.com/x86/movnti
    ("movnti gpr mem", ("", 0)),  # TODO NT-store: what latency to use?
    # https://www.felixcloutier.com/x86/movntpd
    ("movntpd xmm mem", ("", 0)),  # TODO NT-store: what latency to use?
    ("vmovntpd xmm mem", ("", 0)),  # TODO NT-store: what latency to use?
    ("vmovntpd ymm mem", ("", 0)),  # TODO NT-store: what latency to use?
    # https://www.felixcloutier.com/x86/movntps
    ("movntps xmm mem", ("", 0)),  # TODO NT-store: what latency to use?
    ("vmovntps xmm mem", ("", 0)),  # TODO NT-store: what latency to use?
    ("vmovntps ymm mem", ("", 0)),  # TODO NT-store: what latency to use?
    # https://www.felixcloutier.com/x86/movntq
    ("movntq mm mem", ("", 0)),  # TODO NT-store: what latency to use?
    # https://www.felixcloutier.com/x86/movq
    ("movq mm mm", ("", 0)),
    ("movq mem mm", ("", 0)),
    ("movq mm mem", ("", 0)),
    ("movq xmm xmm", ("1*p015", 1)),
    ("movq mem xmm", ("", 0)),
    ("movq xmm mem", ("", 0)),
    ("vmovq xmm xmm", ("1*p015", 1)),
    ("vmovq mem xmm", ("", 0)),
    ("vmovq xmm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movq2dq
    ("movq2dq mm xmm", ("1*p015", 1)),
    # https://www.felixcloutier.com/x86/movs:movsb:movsw:movsd:movsq
    # TODO combined load-store is currently not supported
    # ('movs mem mem', ()),
    # https://www.felixcloutier.com/x86/movsd
    ("movsd xmm xmm", ("1*p5", 1)),
    ("movsd mem xmm", ("", 0)),
    ("movsd xmm mem", ("", 0)),
    ("vmovsd xmm xmm xmm", ("1*p5", 1)),
    ("vmovsd mem xmm", ("", 0)),
    ("vmovsd xmm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movshdup
    ("movshdup xmm xmm", ("1*p5", 1)),
    ("movshdup mem xmm", ("", 0)),
    ("vmovshdup xmm xmm", ("1*p5", 1)),
    ("vmovshdup mem xmm", ("", 0)),
    ("vmovshdup ymm ymm", ("1*p5", 1)),
    ("vmovshdup mem ymm", ("", 0)),
    # https://www.felixcloutier.com/x86/movsldup
    ("movsldup xmm xmm", ("1*p5", 1)),
    ("movsldup mem xmm", ("", 0)),
    ("vmovsldup xmm xmm", ("1*p5", 1)),
    ("vmovsldup mem xmm", ("", 0)),
    ("vmovsldup ymm ymm", ("1*p5", 1)),
    ("vmovsldup mem ymm", ("", 0)),
    # https://www.felixcloutier.com/x86/movss
    ("movss xmm xmm", ("1*p5", 1)),
    ("movss mem xmm", ("", 0)),
    ("vmovss xmm xmm xmm", ("1*p5", 1)),
    ("vmovss mem xmm", ("", 0)),
    ("vmovss xmm xmm", ("1*p5", 1)),
    ("vmovss xmm mem", ("", 0)),
    ("movss mem xmm", ("", 0)),
    # https://www.felixcloutier.com/x86/movsx:movsxd
    ("movsx gpr gpr", ("1*p015", 1)),
    ("movsx mem gpr", ("", 0)),
    ("movsxd gpr gpr", ("", 0)),
    ("movsxd mem gpr", ("", 0)),
    ("movsb gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movsb mem gpr", ("", 0)),  # AT&T version
    ("movsw gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movsw mem gpr", ("", 0)),  # AT&T version
    ("movsl gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movsl mem gpr", ("", 0)),  # AT&T version
    ("movsq gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movsq mem gpr", ("", 0)),  # AT&T version
    # https://www.felixcloutier.com/x86/movupd
    ("movupd xmm xmm", ("1*p5", 1)),
    ("movupd mem xmm", ("", 0)),
    ("movupd xmm mem", ("", 0)),
    ("vmovupd xmm xmm", ("1*p5", 1)),
    ("vmovupd mem xmm", ("", 0)),
    ("vmovupd xmm mem", ("", 0)),
    ("vmovupd ymm ymm", ("1*p5", 1)),
    ("vmovupd mem ymm", ("", 0)),
    ("vmovupd ymm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movups
    ("movups xmm xmm", ("1*p5", 1)),
    ("movups mem xmm", ("", 0)),
    ("movups xmm mem", ("", 0)),
    ("vmovups xmm xmm", ("1*p5", 1)),
    ("vmovups mem xmm", ("", 0)),
    ("vmovups xmm mem", ("", 0)),
    ("vmovups ymm ymm", ("1*p5", 1)),
    ("vmovups mem ymm", ("", 0)),
    ("vmovups ymm mem", ("", 0)),
    # https://www.felixcloutier.com/x86/movzx
    ("movzx gpr gpr", ("1*p015", 1)),
    ("movzx mem gpr", ("", 0)),
    ("movzb gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movzb mem gpr", ("", 0)),  # AT&T version
    ("movzw gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movzw mem gpr", ("", 0)),  # AT&T version
    ("movzl gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movzl mem gpr", ("", 0)),  # AT&T version
    ("movzq gpr gpr", ("1*p015", 1)),  # AT&T version
    ("movzq mem gpr", ("", 0)),  # AT&T version
    # https://www.felixcloutier.com/x86/cmovcc
    ("cmova gpr gpr", ("1*p015+2*p05", 2)),
    ("cmova mem gpr", ("1*p015+2*p05", 2)),
    ("cmovae gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovae mem gpr", ("1*p015+2*p05", 2)),
    ("cmovb gpr gpr", ("1*p015+2*p05", 2)),
    ("cmovb mem gpr", ("1*p015+1*p05", 2)),
    ("cmovbe gpr gpr", ("1*p015+2*p05", 2)),
    ("cmovbe mem gpr", ("1*p015+2*p05", 2)),
    ("cmovc gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovc mem gpr", ("1*p015+1*p05", 2)),
    ("cmove gpr gpr", ("1*p015+1*p05", 2)),
    ("cmove mem gpr", ("1*p015+1*p05", 2)),
    ("cmovg gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovg mem gpr", ("1*p015+1*p05", 2)),
    ("cmovge gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovge mem gpr", ("1*p015+1*p05", 2)),
    ("cmovl gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovl mem gpr", ("1*p015+1*p05", 2)),
    ("cmovle gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovle mem gpr", ("1*p015+1*p05", 2)),
    ("cmovna gpr gpr", ("1*p015+2*p05", 2)),
    ("cmovna mem gpr", ("1*p015+2*p05", 2)),
    ("cmovnae gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnae mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnb gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnb mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnbe gpr gpr", ("1*p015+2*p05", 2)),
    ("cmovnbe mem gpr", ("1*p015+2*p05", 2)),
    ("cmovnb gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnb mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnc gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnc mem gpr", ("1*p015+1*p05", 2)),
    ("cmovne gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovne mem gpr", ("1*p015+1*p05", 2)),
    ("cmovng gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovng mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnge gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnge mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnl gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnl mem gpr", ("1*p015+1*p05", 2)),
    ("cmovno gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovno mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnp gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnp mem gpr", ("1*p015+1*p05", 2)),
    ("cmovns gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovns mem gpr", ("1*p015+1*p05", 2)),
    ("cmovnz gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovnz mem gpr", ("1*p015+1*p05", 2)),
    ("cmovo gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovo mem gpr", ("1*p015+1*p05", 2)),
    ("cmovp gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovp mem gpr", ("1*p015+1*p05", 2)),
    ("cmovpe gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovpe mem gpr", ("1*p015+1*p05", 2)),
    ("cmovpo gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovpo mem gpr", ("1*p015+1*p05", 2)),
    ("cmovs gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovs mem gpr", ("1*p015+1*p05", 2)),
    ("cmovz gpr gpr", ("1*p015+1*p05", 2)),
    ("cmovz mem gpr", ("1*p015+1*p05", 2)),
    # https://www.felixcloutier.com/x86/pmovmskb
    ("pmovmskb mm gpr", ("1*p0", 2)),
    ("pmovmskb xmm gpr", ("1*p0", 2)),
    ("vpmovmskb xmm gpr", ("1*p0", 2)),
    # https://www.felixcloutier.com/x86/pmovsx
    ("pmovsxbw xmm xmm", ("1*p15", 1)),
    ("pmovsxbw mem xmm", ("1*p15", 1)),
    ("pmovsxbd xmm xmm", ("1*p15", 1)),
    ("pmovsxbd mem xmm", ("1*p15", 1)),
    ("pmovsxbq xmm xmm", ("1*p15", 1)),
    ("pmovsxbq mem xmm", ("1*p15", 1)),
    ("vpmovsxbw xmm xmm", ("1*p15", 1)),
    ("vpmovsxbw mem xmm", ("1*p15", 1)),
    ("vpmovsxbd xmm xmm", ("1*p15", 1)),
    ("vpmovsxbd mem xmm", ("1*p15", 1)),
    ("vpmovsxbq xmm xmm", ("1*p15", 1)),
    ("vpmovsxbq mem xmm", ("1*p15", 1)),
    ("vpmovsxbw ymm ymm", ("1*p15", 1)),
    ("vpmovsxbw mem ymm", ("1*p15", 1)),
    ("vpmovsxbd ymm ymm", ("1*p15", 1)),
    ("vpmovsxbd mem ymm", ("1*p15", 1)),
    ("vpmovsxbq ymm ymm", ("1*p15", 1)),
    ("vpmovsxbq mem ymm", ("1*p15", 1)),
    # https://www.felixcloutier.com/x86/pmovzx
    ("pmovzxbw xmm xmm", ("1*p15", 1)),
    ("pmovzxbw mem xmm", ("1*p15", 1)),
    ("vpmovzxbw xmm xmm", ("1*p15", 1)),
    ("vpmovzxbw mem xmm", ("1*p15", 1)),
    ("vpmovzxbw ymm ymm", ("1*p15", 1)),
    ("vpmovzxbw mem ymm", ("1*p15", 1)),
]

ivb_mov_instructions = list(
    OrderedDict(
        snb_mov_instructions
        + [
            # https://www.felixcloutier.com/x86/mov
            ("mov gpr gpr", ("", 0)),
            ("mov imd gpr", ("", 0)),
            # https://www.felixcloutier.com/x86/movapd
            ("movapd xmm xmm", ("", 0)),
            ("vmovapd xmm xmm", ("", 0)),
            ("vmovapd ymm ymm", ("", 0)),
            # https://www.felixcloutier.com/x86/movaps
            ("movaps xmm xmm", ("", 0)),
            ("vmovaps xmm xmm", ("", 0)),
            ("vmovaps ymm ymm", ("", 0)),
            # https://www.felixcloutier.com/x86/movdqa:vmovdqa32:vmovdqa64
            ("movdqa xmm xmm", ("", 0)),
            ("vmovdqa xmm xmm", ("", 0)),
            ("vmovdqa ymm ymm", ("", 0)),
            # https://www.felixcloutier.com/x86/movdqu:vmovdqu8:vmovdqu16:vmovdqu32:vmovdqu64
            ("movdqu xmm xmm", ("", 0)),
            ("vmovdqu xmm xmm", ("", 0)),
            ("vmovdqu ymm ymm", ("", 0)),
            # https://www.felixcloutier.com/x86/movupd
            ("movupd xmm xmm", ("", 0)),
            ("vmovupd xmm xmm", ("", 0)),
            ("vmovupd ymm ymm", ("", 0)),
            # https://www.felixcloutier.com/x86/movupd
            ("movups xmm xmm", ("", 0)),
            ("vmovups xmm xmm", ("", 0)),
            ("vmovups ymm ymm", ("", 0)),
        ]
    ).items()
)

hsw_mov_instructions = list(
    OrderedDict(
        ivb_mov_instructions
        + [
            # https://www.felixcloutier.com/x86/mov
            ("mov imd gpr", ("1*p0156", 1)),
            ("mov gpr gpr", ("1*p0156", 1)),
            ("movabs imd gpr", ("1*p0156", 1)),  # AT&T version
            # https://www.felixcloutier.com/x86/movbe
            ("movbe gpr mem", ("1*p15", 6)),
            ("movbe mem gpr", ("1*p15", 6)),
            # https://www.felixcloutier.com/x86/movmskpd
            ("movmskpd xmm gpr", ("1*p0", 3)),
            ("vmovmskpd xmm gpr", ("1*p0", 3)),
            ("vmovmskpd ymm gpr", ("1*p0", 3)),
            # https://www.felixcloutier.com/x86/movmskps
            ("movmskps xmm gpr", ("1*p0", 3)),
            ("vmovmskps xmm gpr", ("1*p0", 3)),
            ("vmovmskps ymm gpr", ("1*p0", 3)),
            # https://www.felixcloutier.com/x86/movsx:movsxd
            ("movsx gpr gpr", ("1*p0156", 1)),
            ("movsb gpr gpr", ("1*p0156", 1)),  # AT&T version
            ("movsw gpr gpr", ("1*p0156", 1)),  # AT&T version
            ("movsl gpr gpr", ("1*p0156", 1)),  # AT&T version
            ("movsq gpr gpr", ("1*p0156", 1)),  # AT&T version
            # https://www.felixcloutier.com/x86/movzx
            ("movzx gpr gpr", ("1*p0156", 1)),
            ("movzb gpr gpr", ("1*p0156", 1)),  # AT&T version
            ("movzw gpr gpr", ("1*p0156", 1)),  # AT&T version
            ("movzl gpr gpr", ("1*p0156", 1)),  # AT&T version
            ("movzq gpr gpr", ("1*p0156", 1)),  # AT&T version
            # https://www.felixcloutier.com/x86/cmovcc
            ("cmova gpr gpr", ("1*p0156+2*p06", 2)),
            ("cmova mem gpr", ("1*p0156+2*p06", 2)),
            ("cmovae gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovae mem gpr", ("1*p0156+2*p06", 2)),
            ("cmovb gpr gpr", ("1*p0156+2*p06", 2)),
            ("cmovb mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovbe gpr gpr", ("1*p0156+2*p06", 2)),
            ("cmovbe mem gpr", ("1*p0156+2*p06", 2)),
            ("cmovc gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovc mem gpr", ("1*p0156+1*p06", 2)),
            ("cmove gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmove mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovg gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovg mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovge gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovge mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovl gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovl mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovle gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovle mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovna gpr gpr", ("1*p0156+2*p06", 2)),
            ("cmovna mem gpr", ("1*p0156+2*p06", 2)),
            ("cmovnae gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnae mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnb gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnb mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnbe gpr gpr", ("1*p0156+2*p06", 2)),
            ("cmovnbe mem gpr", ("1*p0156+2*p06", 2)),
            ("cmovnb gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnb mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnc gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnc mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovne gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovne mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovng gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovng mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnge gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnge mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnl gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnl mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovno gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovno mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnp gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnp mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovns gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovns mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovnz gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovnz mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovo gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovo mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovp gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovp mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovpe gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovpe mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovpo gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovpo mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovs gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovs mem gpr", ("1*p0156+1*p06", 2)),
            ("cmovz gpr gpr", ("1*p0156+1*p06", 2)),
            ("cmovz mem gpr", ("1*p0156+1*p06", 2)),
            # https://www.felixcloutier.com/x86/pmovmskb
            ("pmovmskb mm gpr", ("1*p0", 3)),
            ("pmovmskb xmm gpr", ("1*p0", 3)),
            ("vpmovmskb xmm gpr", ("1*p0", 3)),
            ("vpmovmskb ymm gpr", ("1*p0", 3)),
            # https://www.felixcloutier.com/x86/pmovsx
            ("pmovsxbw xmm xmm", ("1*p5", 1)),
            ("pmovsxbw mem xmm", ("1*p5", 1)),
            ("pmovsxbd xmm xmm", ("1*p5", 1)),
            ("pmovsxbd mem xmm", ("1*p5", 1)),
            ("pmovsxbq xmm xmm", ("1*p5", 1)),
            ("pmovsxbq mem xmm", ("1*p5", 1)),
            ("vpmovsxbw xmm xmm", ("1*p5", 1)),
            ("vpmovsxbw mem xmm", ("1*p5", 1)),
            ("vpmovsxbd xmm xmm", ("1*p5", 1)),
            ("vpmovsxbd mem xmm", ("1*p5", 1)),
            ("vpmovsxbq xmm xmm", ("1*p5", 1)),
            ("vpmovsxbq mem xmm", ("1*p5", 1)),
            ("vpmovsxbw ymm ymm", ("1*p5", 1)),
            ("vpmovsxbw mem ymm", ("1*p5", 1)),
            ("vpmovsxbd ymm ymm", ("1*p5", 1)),
            ("vpmovsxbd mem ymm", ("1*p5", 1)),
            ("vpmovsxbq ymm ymm", ("1*p5", 1)),
            ("vpmovsxbq mem ymm", ("1*p5", 1)),
            # https://www.felixcloutier.com/x86/pmovzx
            ("pmovzxbw xmm xmm", ("1*p5", 1)),
            ("pmovzxbw mem xmm", ("1*p5", 1)),
            ("vpmovzxbw xmm xmm", ("1*p5", 1)),
            ("vpmovzxbw mem xmm", ("1*p5", 1)),
            ("vpmovzxbw ymm ymm", ("1*p5", 1)),
            ("vpmovzxbw mem ymm", ("1*p5", 1)),
        ]
    ).items()
)

bdw_mov_instructions = list(
    OrderedDict(
        hsw_mov_instructions
        + [
            # https://www.felixcloutier.com/x86/cmovcc
            ("cmova gpr gpr", ("2*p06", 1)),
            ("cmova mem gpr", ("2*p06", 1)),
            ("cmovae gpr gpr", ("1*p06", 1)),
            ("cmovae mem gpr", ("2*p06", 1)),
            ("cmovb gpr gpr", ("2*p06", 1)),
            ("cmovb mem gpr", ("1*p06", 1)),
            ("cmovbe gpr gpr", ("2*p06", 1)),
            ("cmovbe mem gpr", ("2*p06", 1)),
            ("cmovc gpr gpr", ("1*p06", 1)),
            ("cmovc mem gpr", ("1*p06", 1)),
            ("cmove gpr gpr", ("1*p06", 1)),
            ("cmove mem gpr", ("1*p06", 1)),
            ("cmovg gpr gpr", ("1*p06", 1)),
            ("cmovg mem gpr", ("1*p06", 1)),
            ("cmovge gpr gpr", ("1*p06", 1)),
            ("cmovge mem gpr", ("1*p06", 1)),
            ("cmovl gpr gpr", ("1*p06", 1)),
            ("cmovl mem gpr", ("1*p06", 1)),
            ("cmovle gpr gpr", ("1*p06", 1)),
            ("cmovle mem gpr", ("1*p06", 1)),
            ("cmovna gpr gpr", ("2*p06", 1)),
            ("cmovna mem gpr", ("2*p06", 1)),
            ("cmovnae gpr gpr", ("1*p06", 1)),
            ("cmovnae mem gpr", ("1*p06", 1)),
            ("cmovnb gpr gpr", ("1*p06", 1)),
            ("cmovnb mem gpr", ("1*p06", 1)),
            ("cmovnbe gpr gpr", ("2*p06", 1)),
            ("cmovnbe mem gpr", ("2*p06", 1)),
            ("cmovnb gpr gpr", ("1*p06", 1)),
            ("cmovnb mem gpr", ("1*p06", 1)),
            ("cmovnc gpr gpr", ("1*p06", 1)),
            ("cmovnc mem gpr", ("1*p06", 1)),
            ("cmovne gpr gpr", ("1*p06", 1)),
            ("cmovne mem gpr", ("1*p06", 1)),
            ("cmovng gpr gpr", ("1*p06", 1)),
            ("cmovng mem gpr", ("1*p06", 1)),
            ("cmovnge gpr gpr", ("1*p06", 1)),
            ("cmovnge mem gpr", ("1*p06", 1)),
            ("cmovnl gpr gpr", ("1*p06", 1)),
            ("cmovnl mem gpr", ("1*p06", 1)),
            ("cmovno gpr gpr", ("1*p06", 1)),
            ("cmovno mem gpr", ("1*p06", 1)),
            ("cmovnp gpr gpr", ("1*p06", 1)),
            ("cmovnp mem gpr", ("1*p06", 1)),
            ("cmovns gpr gpr", ("1*p06", 1)),
            ("cmovns mem gpr", ("1*p06", 1)),
            ("cmovnz gpr gpr", ("1*p06", 1)),
            ("cmovnz mem gpr", ("1*p06", 1)),
            ("cmovo gpr gpr", ("1*p06", 1)),
            ("cmovo mem gpr", ("1*p06", 1)),
            ("cmovp gpr gpr", ("1*p06", 1)),
            ("cmovp mem gpr", ("1*p06", 1)),
            ("cmovpe gpr gpr", ("1*p06", 1)),
            ("cmovpe mem gpr", ("1*p06", 1)),
            ("cmovpo gpr gpr", ("1*p06", 1)),
            ("cmovpo mem gpr", ("1*p06", 1)),
            ("cmovs gpr gpr", ("1*p06", 1)),
            ("cmovs mem gpr", ("1*p06", 1)),
            ("cmovz gpr gpr", ("1*p06", 1)),
            ("cmovz mem gpr", ("1*p06", 1)),
        ]
    ).items()
)

skx_mov_instructions = list(
    OrderedDict(
        bdw_mov_instructions
        + [
            # https://www.felixcloutier.com/x86/movapd
            # TODO with masking!
            # TODO the following may eliminate or be bound to 1*p0156:
            # ('movapd xmm xmm', ('1*p5', 1)),
            # ('vmovapd xmm xmm', ('1*p5', 1)),
            # ('vmovapd ymm ymm', ('1*p5', 1)),
            ("vmovapd zmm zmm", ("", 0)),
            # https://www.felixcloutier.com/x86/movaps
            # TODO with masking!
            # TODO the following may eliminate or be bound to 1*p0156:
            # ('movaps xmm xmm', ('1*p5', 1)),
            # ('vmovaps xmm xmm', ('1*p5', 1)),
            # ('vmovaps ymm ymm', ('1*p5', 1)),
            ("vmovaps zmm zmm", ("", 0)),
            # https://www.felixcloutier.com/x86/movbe
            ("movbe gpr mem", ("1*p15", 4)),
            ("movbe mem gpr", ("1*p15", 4)),
            # https://www.felixcloutier.com/x86/movddup
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movdqa:vmovdqa32:vmovdqa64
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movdqu:vmovdqu8:vmovdqu16:vmovdqu32:vmovdqu64
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movntdq
            ("vmovntdq zmm mem", ("", 0)),  # TODO NT-store: what latency to use?
            # https://www.felixcloutier.com/x86/movntdqa
            ("vmovntdqa mem zmm", ("", 0)),
            # https://www.felixcloutier.com/x86/movntpd
            ("vmovntpd zmm mem", ("", 0)),  # TODO NT-store: what latency to use?
            # https://www.felixcloutier.com/x86/movntps
            ("vmovntps zmm mem", ("", 0)),  # TODO NT-store: what latency to use?
            # https://www.felixcloutier.com/x86/movq2dq
            ("movq2dq mm xmm", ("1*p0+1*p015", 1)),
            # https://www.felixcloutier.com/x86/movsd
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movshdup
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movsldup
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movss
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movupd
            # TODO with masking!
            # https://www.felixcloutier.com/x86/movups
            # TODO with masking!
            # https://www.felixcloutier.com/x86/pmovsx
            # TODO with masking!
            ("vpmovsxbw ymm zmm", ("1*p5", 3)),
            ("vpmovsxbw mem zmm", ("1*p5", 1)),
        ]
    ).items()
)

csx_mov_instructions = OrderedDict(skx_mov_instructions + []).items()


def get_description(arch, rhs_comment=None):
    descriptions = {
        "snb": "\n".join([np7.process_item(*item) for item in snb_mov_instructions]),
        "ivb": "\n".join([np7.process_item(*item) for item in ivb_mov_instructions]),
        "hsw": "\n".join([p7.process_item(*item) for item in hsw_mov_instructions]),
        "bdw": "\n".join([p7.process_item(*item) for item in bdw_mov_instructions]),
        "skx": "\n".join([p7.process_item(*item) for item in skx_mov_instructions]),
        "csx": "\n".join([p7.process_item(*item) for item in csx_mov_instructions]),
    }

    description = descriptions[arch]

    if rhs_comment is not None:
        max_length = max([len(line) for line in descriptions[arch].split("\n")])

        commented_description = ""
        for line in descriptions[arch].split("\n"):
            commented_description += ("{:<" + str(max_length) + "}  # {}\n").format(
                line, rhs_comment
            )
        description = commented_description

    return description


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: {} (snb|ivb|hsw|bdw|skx|csx)".format(sys.argv[0]))
        sys.exit(0)

    try:
        print(get_description(sys.argv[1], rhs_comment=" ".join(sys.argv)))
    except KeyError:
        print("Unknown architecture.")
        sys.exit(1)
