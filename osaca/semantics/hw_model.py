#!/usr/bin/env python3

import hashlib
import os
import pickle
import re
import string
from collections import defaultdict
from itertools import product
from pathlib import Path

import ruamel.yaml
from osaca import __version__, utils
from osaca.parser import ParserX86ATT
from osaca.parser.instruction_form import InstructionForm
from osaca.parser.operand import Operand
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.identifier import IdentifierOperand
from osaca.parser.condition import ConditionOperand
from osaca.parser.flag import FlagOperand
from osaca.parser.prefetch import PrefetchOperand
from ruamel.yaml.compat import StringIO


class MachineModel(object):
    WILDCARD = "*"
    INTERNAL_VERSION = 1  # increase whenever self._data format changes to invalidate cache!
    _runtime_cache = {}

    def __init__(self, arch=None, path_to_yaml=None, isa=None, lazy=False):
        if not arch and not path_to_yaml:
            if not isa:
                raise ValueError("One of arch, path_to_yaml and isa must be specified")
            self._data = {
                "osaca_version": str(__version__),
                "micro_architecture": None,
                "arch_code": None,
                "isa": isa,
                "ROB_size": None,
                "retired_uOps_per_cycle": None,
                "scheduler_size": None,
                "hidden_loads": None,
                "load_latency": {},
                "load_throughput": [
                    {
                        "base": b,
                        "index": i,
                        "offset": o,
                        "scale": s,
                    }
                    for b, i, o, s in product(["gpr"], ["gpr", None], ["imd", None], [1, 8])
                ],
                "load_throughput_default": [],
                "store_throughput": [],
                "store_throughput_default": [],
                "store_to_load_forward_latency": None,
                "ports": [],
                "port_model_scheme": None,
                "instruction_forms": [],
                "instruction_forms_dict": defaultdict(list),
            }
        else:
            if arch and path_to_yaml:
                raise ValueError("Only one of arch and path_to_yaml is allowed.")
            self._path = path_to_yaml
            self._arch = arch
            if arch:
                self._arch = arch.lower()
                self._path = utils.find_datafile(self._arch + ".yml")
            # Check runtime cache
            if self._path in MachineModel._runtime_cache and not lazy:
                self._data = MachineModel._runtime_cache[self._path]
            # check if file is cached
            cached = self._get_cached(self._path) if not lazy else False
            if cached:
                self._data = cached
            else:
                yaml = self._create_yaml_object()
                # otherwise load
                with open(self._path, "r") as f:
                    if not lazy:
                        self._data = yaml.load(f)
                    else:
                        file_content = ""
                        line = f.readline()
                        while "instruction_forms:" not in line:
                            file_content += line
                            line = f.readline()
                        self._data = yaml.load(file_content)
                        self._data["instruction_forms"] = []
                # separate multi-alias instruction forms
                for entry in [
                    x for x in self._data["instruction_forms"] if isinstance(x["name"], list)
                ]:
                    for name in entry["name"]:
                        new_entry = {"name": name}
                        for k in [x for x in entry.keys() if x != "name"]:
                            new_entry[k] = entry[k]
                        self._data["instruction_forms"].append(new_entry)
                    # remove old entry
                    self._data["instruction_forms"].remove(entry)
                # Normalize instruction_form names (to UPPERCASE) and build dict for faster access:
                self._data["instruction_forms_dict"] = defaultdict(list)

                for iform in self._data["instruction_forms"]:
                    iform["name"] = iform["name"].upper()
                    if iform["operands"] != []:
                        new_operands = []
                        # Change operand types from dicts to classes
                        for o in iform["operands"]:
                            self.operand_to_class(o, new_operands)
                        iform["operands"] = new_operands
                    # Do the same for hidden operands
                    if "hidden_operands" in iform:
                        new_operands = []
                        # Change operand types from dicts to classes
                        for o in iform["hidden_operands"]:
                            self.operand_to_class(o, new_operands)
                        iform["hidden_operands"] = new_operands

                    # Change dict iform style to class style
                    new_iform = InstructionForm(
                        mnemonic=iform["name"].upper() if "name" in iform else None,
                        operands=iform["operands"] if "operands" in iform else [],
                        hidden_operands=(
                            iform["hidden_operands"] if "hidden_operands" in iform else []
                        ),
                        directive_id=iform["directive"] if "directive" in iform else None,
                        comment_id=iform["comment"] if "comment" in iform else None,
                        line=iform["line"] if "line" in iform else None,
                        line_number=iform["line_number"] if "line_number" in iform else None,
                        latency=iform["latency"] if "latency" in iform else None,
                        throughput=iform["throughput"] if "throughput" in iform else None,
                        uops=iform["uops"] if "uops" in iform else None,
                        port_pressure=iform["port_pressure"] if "port_pressure" in iform else None,
                        operation=iform["operation"] if "operation" in iform else None,
                        breaks_dependency_on_equal_operands=(
                            iform["breaks_dependency_on_equal_operands"]
                            if "breaks_dependency_on_equal_operands" in iform
                            else False
                        ),
                        semantic_operands=(
                            iform["semantic_operands"]
                            if "semantic_operands" in iform
                            else {"source": [], "destination": [], "src_dst": []}
                        ),
                    )
                    # List containing classes with same name/instruction
                    self._data["instruction_forms_dict"][iform["name"]].append(new_iform)
                self._data["internal_version"] = self.INTERNAL_VERSION

                # Convert load and store throughput memory operands to classes
                new_throughputs = []
                if "load_throughput" in self._data:
                    for m in self._data["load_throughput"]:
                        new_throughputs.append(
                            (
                                MemoryOperand(
                                    base=m["base"],
                                    offset=m["offset"],
                                    scale=m["scale"],
                                    index=m["index"],
                                    dst=m["dst"] if "dst" in m else None,
                                ),
                                m["port_pressure"],
                            )
                        )
                    self._data["load_throughput"] = new_throughputs

                new_throughputs = []
                if "store_throughput" in self._data:
                    for m in self._data["store_throughput"]:
                        new_throughputs.append(
                            (
                                MemoryOperand(
                                    base=m["base"],
                                    offset=m["offset"],
                                    scale=m["scale"],
                                    index=m["index"],
                                    src=m["src"] if "src" in m else None,
                                ),
                                m["port_pressure"],
                            )
                        )
                    self._data["store_throughput"] = new_throughputs

                if not lazy:
                    # cache internal representation for future use
                    self._write_in_cache(self._path)
            # Store in runtime cache
            if not lazy:
                MachineModel._runtime_cache[self._path] = self._data

    def operand_to_class(self, o, new_operands):
        """Convert an operand from dict type to class"""
        if o["class"] == "register":
            new_operands.append(
                RegisterOperand(
                    name=o["name"] if "name" in o else None,
                    prefix=o["prefix"] if "prefix" in o else None,
                    shape=o["shape"] if "shape" in o else None,
                    mask=o["mask"] if "mask" in o else False,
                    pre_indexed=o["pre_indexed"] if "pre_indexed" in o else False,
                    post_indexed=o["post_indexed"] if "post_indexed" in o else False,
                    source=o["source"] if "source" in o else False,
                    destination=o["destination"] if "destination" in o else False,
                )
            )
        elif o["class"] == "memory":
            if isinstance(o["base"], dict):
                o["base"] = RegisterOperand(name=o["base"]["name"])
            if isinstance(o["index"], dict):
                o["index"] = RegisterOperand(
                    name=o["index"]["name"],
                    prefix=o["index"]["prefix"] if "prefix" in o["index"] else None,
                )
            new_operands.append(
                MemoryOperand(
                    base=o["base"],
                    offset=o["offset"],
                    index=o["index"],
                    scale=o["scale"],
                    source=o["source"] if "source" in o else False,
                    destination=o["destination"] if "destination" in o else False,
                    pre_indexed=o["pre_indexed"] if "pre_indexed" in o else False,
                    post_indexed=o["post_indexed"] if "post_indexed" in o else False,
                )
            )
        elif o["class"] == "immediate":
            new_operands.append(
                ImmediateOperand(
                    imd_type=o["imd"],
                    source=o["source"] if "source" in o else False,
                    destination=o["destination"] if "destination" in o else False,
                )
            )
        elif o["class"] == "identifier":
            new_operands.append(
                IdentifierOperand(
                    name=o["name"] if "name" in o else None,
                    source=o["source"] if "source" in o else False,
                    destination=o["destination"] if "destination" in o else False,
                )
            )
        elif o["class"] == "condition":
            new_operands.append(
                ConditionOperand(
                    ccode=o["ccode"].upper(),
                    source=o["source"] if "source" in o else False,
                    destination=o["destination"] if "destination" in o else False,
                )
            )
        elif o["class"] == "flag":
            new_operands.append(
                FlagOperand(
                    name=o["name"],
                    source=o["source"] if "source" in o else False,
                    destination=o["destination"] if "destination" in o else False,
                )
            )
        elif o["class"] == "prfop":
            new_operands.append(
                PrefetchOperand(
                    type_id=o["type"] if "type" in o else None,
                    target=o["target"] if "target" in o else None,
                    policy=o["policy"] if "policy" in o else None,
                )
            )
        else:
            new_operands.append(o)

    def get(self, key, default=None):
        """Return config entry for key or default/None."""
        return self._data.get(key, default)

    def __getitem__(self, key):
        """Return configuration entry."""
        return self._data[key]

    def __contains__(self, key):
        """Return true if configuration key is present."""
        return key in self._data

    ######################################################

    def get_instruction(self, name, operands):
        """Find and return instruction data from name and operands."""
        # For use with dict instead of list as DB
        if name is None:
            return None
        name_matched_iforms = self._data["instruction_forms_dict"].get(name.upper(), [])

        try:
            return next(
                instruction_form
                for instruction_form in name_matched_iforms
                if self._match_operands(
                    instruction_form.operands,
                    operands,
                )
            )
        except StopIteration:
            return None
        except TypeError as e:
            print("\nname: {}\noperands: {}".format(name, operands))
            raise TypeError from e

    def average_port_pressure(self, port_pressure, option=0):
        """Construct average port pressure list from instruction data."""
        port_list = self._data["ports"]
        average_pressure = [0.0] * len(port_list)
        # if there are multiple port utilization options and none is selected, choose first one
        if isinstance(port_pressure, dict):
            used_pp = port_pressure[option]
        else:
            used_pp = port_pressure
        for cycles, ports in used_pp:
            for p in ports:
                try:
                    average_pressure[port_list.index(p)] += cycles / len(ports)
                except ValueError as e:
                    raise KeyError("Port {!r} not in port list.".format(p)) from e
        return average_pressure

    def set_instruction(
        self,
        mnemonic,
        operands=None,
        latency=None,
        port_pressure=None,
        throughput=None,
        uops=None,
    ):
        """Import instruction form information."""
        # If it already exists. Overwrite information.
        instr_data = self.get_instruction(mnemonic, operands)
        if instr_data is None:
            instr_data = InstructionForm()
            self._data["instruction_forms"].append(instr_data)
            self._data["instruction_forms_dict"][mnemonic].append(instr_data)

        instr_data.mnemonic = mnemonic
        instr_data.operands = operands
        instr_data.latency = latency
        instr_data.port_pressure = port_pressure
        instr_data.throughput = throughput
        instr_data.uops = uops

    def set_instruction_entry(self, entry):
        """Import instruction as entry object form information."""
        if entry.mnemonic is None and entry.operands == []:
            raise KeyError
        self.set_instruction(
            entry.mnemonic,
            entry.operands,
            entry.latency,
            entry.port_pressure,
            entry.throughput,
            entry.uops,
        )

    def add_port(self, port):
        """Add port in port model of current machine model."""
        if port not in self._data["ports"]:
            self._data["ports"].append(port)

    def get_ISA(self):
        """Return ISA of :class:`MachineModel`."""
        return self._data["isa"].lower()

    def get_arch(self):
        """Return micro-architecture code of :class:`MachineModel`."""
        return self._data["arch_code"].lower()

    def get_ports(self):
        """Return port model of :class:`MachineModel`."""
        return self._data["ports"]

    def has_hidden_loads(self):
        """Return if model has hidden loads."""
        if "hidden_loads" in self._data:
            return self._data["hidden_loads"]
        return False

    def get_load_latency(self, reg_type):
        """Return load latency for given register type."""
        return self._data["load_latency"][reg_type] if self._data["load_latency"][reg_type] else 0

    def get_load_throughput(self, memory):
        """Return load thorughput for given register type."""
        ld_tp = [m for m in self._data["load_throughput"] if self._match_mem_entries(memory, m[0])]
        if len(ld_tp) > 0:
            return ld_tp.copy()
        return [(memory, self._data["load_throughput_default"].copy())]

    def get_store_latency(self, reg_type):
        """Return store latency for given register type."""
        # assume 0 for now, since load-store-dependencies currently not detectable
        return 0

    def get_store_throughput(self, memory, src_reg=None):
        """Return store throughput for a given destination and register type."""
        st_tp = [
            m for m in self._data["store_throughput"] if self._match_mem_entries(memory, m[0])
        ]
        if src_reg is not None:
            st_tp = [
                tp
                for tp in st_tp
                if tp[0].src is not None
                and self._check_operands(src_reg, RegisterOperand(name=tp[0].src))
            ]
        if len(st_tp) > 0:
            return st_tp.copy()
        return [(memory, self._data["store_throughput_default"].copy())]

    def _match_mem_entries(self, mem, i_mem):
        """Check if memory addressing ``mem`` and ``i_mem`` are of the same type."""
        if self._data["isa"].lower() == "aarch64":
            return self._is_AArch64_mem_type(i_mem, mem)
        if self._data["isa"].lower() == "x86":
            return self._is_x86_mem_type(i_mem, mem)

    def get_data_ports(self):
        """Return all data ports (i.e., ports with D-suffix) of current model."""
        data_port = re.compile(r"^[0-9]+D$")
        data_ports = [x for x in filter(data_port.match, self._data["ports"])]
        return data_ports

    @staticmethod
    def get_isa_for_arch(arch):
        """Return ISA for given micro-arch ``arch``."""
        arch_dict = {
            "a64fx": "aarch64",
            "tsv110": "aarch64",
            "a72": "aarch64",
            "tx2": "aarch64",
            "n1": "aarch64",
            "m1": "aarch64",
            "v2": "aarch64",
            "zen1": "x86",
            "zen+": "x86",
            "zen2": "x86",
            "zen3": "x86",
            "zen4": "x86",
            "con": "x86",  # Intel Conroe
            "wol": "x86",  # Intel Wolfdale
            "snb": "x86",
            "ivb": "x86",
            "hsw": "x86",
            "bdw": "x86",
            "skl": "x86",
            "skx": "x86",
            "csx": "x86",
            "wsm": "x86",
            "nhm": "x86",
            "kbl": "x86",
            "cnl": "x86",
            "cfl": "x86",
            "icl": "x86",
            "icx": "x86",
            "spr": "x86",
        }
        arch = arch.lower()
        if arch in arch_dict:
            return arch_dict[arch].lower()
        else:
            raise ValueError("Unknown architecture {!r}.".format(arch))

    def class_to_dict(self, op):
        """Need to convert operand classes to dicts for the dump. Memory operand types may have their index/base/offset as a register operand/"""
        if isinstance(op, Operand):
            dict_op = dict(
                (key.lstrip("_"), value)
                for key, value in op.__dict__.items()
                if not callable(value) and not key.startswith("__")
            )
            if isinstance(op, MemoryOperand):
                if isinstance(dict_op["index"], Operand):
                    dict_op["index"] = dict(
                        (key.lstrip("_"), value)
                        for key, value in dict_op["index"].__dict__.items()
                        if not callable(value) and not key.startswith("__")
                    )
                if isinstance(dict_op["offset"], Operand):
                    dict_op["offset"] = dict(
                        (key.lstrip("_"), value)
                        for key, value in dict_op["offset"].__dict__.items()
                        if not callable(value) and not key.startswith("__")
                    )
                if isinstance(dict_op["base"], Operand):
                    dict_op["base"] = dict(
                        (key.lstrip("_"), value)
                        for key, value in dict_op["base"].__dict__.items()
                        if not callable(value) and not key.startswith("__")
                    )
            return dict_op
        return op

    def dump(self, stream=None):
        """Dump machine model to stream or return it as a ``str`` if no stream is given."""
        # Replace instruction form's port_pressure with styled version for RoundtripDumper
        formatted_instruction_forms = []
        for instruction_form in self._data["instruction_forms"]:
            if isinstance(instruction_form, InstructionForm):
                instruction_form = dict(
                    (key.lstrip("_"), value)
                    for key, value in instruction_form.__dict__.items()
                    if not callable(value) and not key.startswith("__")
                )
            if instruction_form["port_pressure"] is not None:
                cs = ruamel.yaml.comments.CommentedSeq(instruction_form["port_pressure"])
                cs.fa.set_flow_style()
                instruction_form["port_pressure"] = cs
            dict_operands = []
            for op in instruction_form["operands"]:
                dict_operands.append(self.class_to_dict(op))
            instruction_form["operands"] = dict_operands
            formatted_instruction_forms.append(instruction_form)

        # Replace load_throughput with styled version for RoundtripDumper
        formatted_load_throughput = []
        for lt in self._data["load_throughput"]:
            cm = self.class_to_dict(lt[0])
            cm["port_pressure"] = lt[1]
            cm = ruamel.yaml.comments.CommentedMap(cm)
            cm.fa.set_flow_style()
            formatted_load_throughput.append(cm)

        # Replace store_throughput with styled version for RoundtripDumper
        formatted_store_throughput = []
        for st in self._data["store_throughput"]:
            cm = self.class_to_dict(st[0])
            cm["port_pressure"] = st[1]
            cm = ruamel.yaml.comments.CommentedMap(cm)
            cm.fa.set_flow_style()
            formatted_store_throughput.append(cm)

        # Create YAML object
        yaml = self._create_yaml_object()
        if not stream:
            stream = StringIO()

        yaml.dump(
            {
                k: v
                for k, v in self._data.items()
                if k
                not in [
                    "instruction_forms",
                    "instruction_forms_dict",
                    "load_throughput",
                    "store_throughput",
                    "internal_version",
                ]
            },
            stream,
        )

        yaml.dump({"load_throughput": formatted_load_throughput}, stream)
        yaml.dump({"store_throughput": formatted_store_throughput}, stream)
        yaml.dump({"instruction_forms": formatted_instruction_forms}, stream)

        if isinstance(stream, StringIO):
            return stream.getvalue()

    ######################################################

    def _get_cached(self, filepath):
        """
        Check if machine model is cached and if so, load it.

        :param filepath: path to check for cached machine model
        :type filepath: str
        :returns: cached DB if existing, `False` otherwise
        """
        p = Path(filepath)
        hexhash = hashlib.sha256(p.read_bytes()).hexdigest()

        # 1. companion cachefile: same location, with '.<name>_<sha512hash>.pickle'
        companion_cachefile = p.with_name("." + p.stem + "_" + hexhash).with_suffix(".pickle")
        if companion_cachefile.exists():
            # companion file (must be up-to-date, due to equal hash)
            with companion_cachefile.open("rb") as f:
                data = pickle.load(f)
            if data.get("internal_version") == self.INTERNAL_VERSION:
                return data

        # 2. home cachefile: ~/.osaca/cache/<name>_<sha512hash>.pickle
        home_cachefile = (Path(utils.CACHE_DIR) / (p.stem + "_" + hexhash)).with_suffix(".pickle")
        if home_cachefile.exists():
            # home file (must be up-to-date, due to equal hash)
            with home_cachefile.open("rb") as f:
                data = pickle.load(f)
            if data.get("internal_version") == self.INTERNAL_VERSION:
                return data
        return False

    def _write_in_cache(self, filepath):
        """
        Write machine model to cache

        :param filepath: path to store DB
        :type filepath: str
        """
        p = Path(filepath)
        hexhash = hashlib.sha256(p.read_bytes()).hexdigest()
        # 1. companion cachefile: same location, with '.<name>_<sha512hash>.pickle'
        companion_cachefile = p.with_name("." + p.stem + "_" + hexhash).with_suffix(".pickle")
        if os.access(str(companion_cachefile.parent), os.W_OK):
            with companion_cachefile.open("wb") as f:
                pickle.dump(self._data, f)
                return

        # 2. home cachefile: ~/.osaca/cache/<name>_<sha512hash>.pickle
        cache_dir = Path(utils.CACHE_DIR)
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except OSError:
            return
        home_cachefile = (cache_dir / (p.stem + "_" + hexhash)).with_suffix(".pickle")
        if os.access(str(home_cachefile.parent), os.W_OK):
            with home_cachefile.open("wb") as f:
                pickle.dump(self._data, f)

    def _get_key(self, name, operands):
        """Get unique instruction form key for dict DB."""
        key_string = name.lower() + "-"
        if operands is None:
            return key_string[:-1]
        key_string += "_".join([self._get_operand_hash(op) for op in operands])
        return key_string

    def _get_operand_hash(self, operand):
        """Get unique key for operand for dict DB"""
        operand_string = ""
        if "class" in operand:
            # DB entry
            opclass = operand["class"]
        else:
            # parsed instruction
            opclass = list(operand.keys())[0]
            operand = operand[opclass]
        if opclass == "immediate":
            # Immediate
            operand_string += "i"
        elif opclass == "register":
            # Register
            if "prefix" in operand:
                operand_string += operand["prefix"]
                operand_string += operand["shape"] if "shape" in operand else ""
            elif "name" in operand:
                operand_string += "r" if operand["name"] == "gpr" else operand["name"][0]
        elif opclass == "memory":
            # Memory
            operand_string += "m"
            operand_string += "b" if operand["base"] is not None else ""
            operand_string += "o" if operand["offset"] is not None else ""
            operand_string += "i" if operand["index"] is not None else ""
            operand_string += (
                "s" if operand["scale"] == self.WILDCARD or operand["scale"] > 1 else ""
            )
            if "pre_indexed" in operand:
                operand_string += "r" if operand["pre_indexed"] else ""
                operand_string += "p" if operand["post_indexed"] else ""
        return operand_string

    def _create_db_operand_aarch64(self, operand):
        """Create instruction form operand for DB out of operand string."""
        if operand == "i":
            return ImmediateOperand(imd_type="int")
        elif operand in "wxbhsdq":
            return RegisterOperand(prefix=operand)
        elif operand.startswith("v"):
            return RegisterOperand(prefix="v", shape=operand[1:2])
        elif operand.startswith("m"):
            return MemoryOperand(
                base="x" if "b" in operand else None,
                offset="imd" if "o" in operand else None,
                index="gpr" if "i" in operand else None,
                scale=8 if "s" in operand else 1,
                pre_indexed=True if "r" in operand else False,
                post_indexed=True if "p" in operand else False,
            )
        else:
            raise ValueError("Parameter {} is not a valid operand code".format(operand))

    def _create_db_operand_x86(self, operand):
        """Create instruction form operand for DB out of operand string."""
        if operand == "r":
            return RegisterOperand(name="gpr")
        elif operand in "xyz":
            return RegisterOperand(name=operand + "mm")
        elif operand == "i":
            return ImmediateOperand(imd_type="int")
        elif operand.startswith("m"):
            return MemoryOperand(
                base="gpr" if "b" in operand else None,
                offset="imd" if "o" in operand else None,
                index="gpr" if "i" in operand else None,
                scale=8 if "s" in operand else 1,
            )
        else:
            raise ValueError("Parameter {} is not a valid operand code".format(operand))

    def _check_for_duplicate(self, name, operands):
        """
        Check if instruction form exists at least twice in DB.

        :param str name: mnemonic of instruction form
        :param list operands: instruction form operands

        :returns: `True`, if duplicate exists, `False` otherwise
        """
        matches = [
            instruction_form
            for instruction_form in self._data["instruction_forms"]
            if instruction_form["name"].lower() == name.lower()
            and self._match_operands(instruction_form["operands"], operands)
        ]
        if len(matches) > 1:
            return True
        return False

    def _match_operands(self, i_operands, operands):
        """Check if all operand types of ``i_operands`` and ``operands`` match."""
        operands_ok = True
        if len(operands) != len(i_operands):
            return False
        for idx, operand in enumerate(operands):
            i_operand = i_operands[idx]
            operands_ok = operands_ok and self._check_operands(i_operand, operand)
        if operands_ok:
            return True
        else:
            return False

    def _check_operands(self, i_operand, operand):
        """Check if the types of operand ``i_operand`` and ``operand`` match."""
        # check for wildcard
        if isinstance(operand, dict) and self.WILDCARD in operand:
            if isinstance(i_operand, RegisterOperand):
                return True
            else:
                return False
        if self._data["isa"].lower() == "aarch64":
            return self._check_AArch64_operands(i_operand, operand)
        if self._data["isa"].lower() == "x86":
            return self._check_x86_operands(i_operand, operand)

    def _check_AArch64_operands(self, i_operand, operand):
        """Check if the types of operand ``i_operand`` and ``operand`` match."""
        # if "class" in operand:
        # compare two DB entries
        #    return self._compare_db_entries(i_operand, operand)
        # TODO support class wildcards
        # register
        if isinstance(operand, RegisterOperand):
            if not isinstance(i_operand, RegisterOperand):
                return False
            return self._is_AArch64_reg_type(i_operand, operand)
        # memory
        if isinstance(operand, MemoryOperand):
            if not isinstance(i_operand, MemoryOperand):
                return False
            return self._is_AArch64_mem_type(i_operand, operand)
        # immediate
        if isinstance(i_operand, ImmediateOperand) and i_operand.imd_type == self.WILDCARD:
            return isinstance(operand, ImmediateOperand) and (operand.value is not None)

        if isinstance(i_operand, ImmediateOperand) and i_operand.imd_type == "int":
            return (
                isinstance(operand, ImmediateOperand)
                and operand.imd_type == "int"
                and operand.value is not None
            )

        if isinstance(i_operand, ImmediateOperand) and i_operand.imd_type == "float":
            return (
                isinstance(operand, ImmediateOperand)
                and operand.imd_type == "float"
                and operand.value is not None
            )

        if isinstance(i_operand, ImmediateOperand) and i_operand.imd_type == "double":
            return (
                isinstance(operand, ImmediateOperand)
                and operand.imd_type == "double"
                and operand.value is not None
            )

        # identifier
        if isinstance(operand, IdentifierOperand) or (
            isinstance(operand, ImmediateOperand) and operand.identifier is not None
        ):
            return isinstance(i_operand, IdentifierOperand)
        # prefetch option
        if isinstance(operand, PrefetchOperand):
            return isinstance(i_operand, PrefetchOperand)
        # condition
        if isinstance(operand, ConditionOperand):
            if isinstance(i_operand, ConditionOperand):
                return (i_operand.ccode == self.WILDCARD) or (i_operand.ccode == operand.ccode)
        # no match
        return False

    def _check_x86_operands(self, i_operand, operand):
        """Check if the types of operand ``i_operand`` and ``operand`` match."""
        # if "class" in operand.name:
        # compare two DB entries
        #    return self._compare_db_entries(i_operand, operand)
        # register
        if isinstance(operand, RegisterOperand):
            if not isinstance(i_operand, RegisterOperand):
                return False
            return self._is_x86_reg_type(i_operand, operand, consider_masking=False)
        # memory
        if isinstance(operand, MemoryOperand):
            if not isinstance(i_operand, MemoryOperand):
                return False
            return self._is_x86_mem_type(i_operand, operand)
        # immediate
        if isinstance(operand, ImmediateOperand):
            # if "immediate" in operand.name or operand.value != None:
            return isinstance(i_operand, ImmediateOperand) and i_operand.imd_type == "int"
        # identifier (e.g., labels)
        if isinstance(operand, IdentifierOperand):
            return isinstance(i_operand, IdentifierOperand)
        return self._compare_db_entries(i_operand, operand)

    def _compare_db_entries(self, operand_1, operand_2):
        """Check if operand types in DB format (i.e., not parsed) match."""
        return True
        operand_attributes = list(
            filter(
                lambda x: True if x != "source" and x != "destination" else False,
                operand_1,
            )
        )
        for key in operand_attributes:
            try:
                if operand_1[key] != operand_2[key] and not any(
                    [x == self.WILDCARD for x in [operand_1[key], operand_2[key]]]
                ):
                    return False
            except KeyError:
                return False
        return True

    def _is_AArch64_reg_type(self, i_reg, reg):
        """Check if register type match."""
        # check for wildcards
        if reg.prefix == self.WILDCARD or i_reg.prefix == self.WILDCARD:
            if reg.shape is not None:
                if i_reg.shape is not None and (
                    reg.shape == i_reg.shape or self.WILDCARD in (reg.shape + i_reg.shape)
                ):
                    return True
                return False
            return True
        # check for prefix and shape
        if reg.prefix != i_reg.prefix:
            return False
        if reg.shape is not None:
            if i_reg.shape is not None and (
                reg.shape == i_reg.shape or self.WILDCARD in (reg.shape + i_reg.shape)
            ):
                return True
            return False
        if reg.lanes is not None:
            if i_reg.lanes is not None and (
                reg.lanes == i_reg.lanes or self.WILDCARD in (reg.lanes + i_reg.lanes)
            ):
                return True
            return False
        return True

    def _is_x86_reg_type(self, i_reg, reg, consider_masking=False):
        """Check if register type match."""
        if reg is None:
            if i_reg is None:
                return True
            return False
        if isinstance(i_reg, RegisterOperand):
            i_reg_name = i_reg.name
        else:
            i_reg_name = i_reg
        # check for wildcards
        if isinstance(reg, str):
            return False
        if i_reg_name is None and reg.name is None:
            return True
        if i_reg_name == self.WILDCARD or reg.name == self.WILDCARD:
            return True
        # differentiate between vector registers (mm, xmm, ymm, zmm) and others (gpr)
        parser_x86 = ParserX86ATT()
        if parser_x86.is_vector_register(reg):
            if reg.name.rstrip(string.digits).lower() == i_reg_name:
                # Consider masking and zeroing for AVX512
                if consider_masking:
                    mask_ok = zero_ok = True
                    if reg.mask is not None or i_reg.mask is not None:
                        # one instruction is missing the masking while the other has it
                        mask_ok = False
                        # check for wildcard
                        if (
                            (
                                reg.mask is not None
                                and reg.mask.rstrip(string.digits).lower() == i_reg.mask
                            )
                            or reg.mask == self.WILDCARD
                            or i_reg.mask == self.WILDCARD
                        ):
                            mask_ok = True
                        if bool(reg.zeroing) ^ bool("zeroing" in i_reg):
                            # one instruction is missing zeroing while the other has it
                            zero_ok = False
                            # check for wildcard
                            if i_reg.zeroing == self.WILDCARD or reg.zeroing == self.WILDCARD:
                                zero_ok = True
                        if not mask_ok or not zero_ok:
                            return False
                return True
        else:
            if reg.name.rstrip(string.digits).lower() == i_reg_name:
                return True
            if i_reg_name == "gpr":
                return True
        return False

    def _is_AArch64_mem_type(self, i_mem, mem):
        """Check if memory addressing type match."""
        if (
            # check base
            (
                (mem.base is None and i_mem.base is None)
                or i_mem.base == self.WILDCARD
                or (isinstance(mem.base, RegisterOperand) and (mem.base.prefix == i_mem.base))
            )
            # check offset
            and (
                mem.offset == i_mem.offset
                or i_mem.offset == self.WILDCARD
                or (
                    mem.offset is not None
                    and isinstance(mem.offset, IdentifierOperand)
                    and isinstance(i_mem.offset, IdentifierOperand)
                )
                or (
                    mem.offset is not None
                    and isinstance(mem.offset, ImmediateOperand)
                    and i_mem.offset == "imd"
                )
            )
            # check index
            and (
                mem.index == i_mem.index
                or i_mem.index == self.WILDCARD
                or (
                    mem.index is not None
                    and mem.index.prefix is not None
                    and mem.index.prefix == i_mem.index
                )
            )
            # check scale
            and (
                mem.scale == i_mem.scale
                or i_mem.scale == self.WILDCARD
                or (mem.scale != 1 and i_mem.scale != 1)
            )
            # check pre-indexing
            and (i_mem.pre_indexed == self.WILDCARD or mem.pre_indexed == i_mem.pre_indexed)
            # check post-indexing
            and (
                i_mem.post_indexed == self.WILDCARD
                or mem.post_indexed == i_mem.post_indexed
                or (isinstance(mem.post_indexed, dict) and i_mem.post_indexed)
            )
        ):
            return True
        return False

    def _is_x86_mem_type(self, i_mem, mem):
        """Check if memory addressing type match."""
        if (
            # check base
            (
                (mem.base is None and i_mem.base is None)
                or i_mem.base == self.WILDCARD
                or self._is_x86_reg_type(i_mem.base, mem.base)
            )
            # check offset
            and (
                mem.offset == i_mem.offset
                or i_mem.offset == self.WILDCARD
                or (
                    mem.offset is not None
                    and isinstance(mem.offset, IdentifierOperand)
                    and isinstance(i_mem.offset, IdentifierOperand)
                )
                or (
                    mem.offset is not None
                    and isinstance(mem.offset, ImmediateOperand)
                    and (
                        i_mem.offset == "imd" or (i_mem.offset is None and mem.offset.value == "0")
                    )
                )
                or (isinstance(mem.offset, IdentifierOperand) and i_mem.offset == "id")
            )
            # check index
            and (
                mem.index == i_mem.index
                or i_mem.index == self.WILDCARD
                or (
                    mem.index is not None
                    # and mem.index.name != None
                    and self._is_x86_reg_type(i_mem.index, mem.index)
                )
            )
            # check scale
            and (
                mem.scale == i_mem.scale
                or i_mem.scale == self.WILDCARD
                or (mem.scale != 1 and i_mem.scale != 1)
            )
        ):
            return True
        return False

    def _create_yaml_object(self):
        """Create YAML object for parsing and dumping DB"""
        yaml_obj = ruamel.yaml.YAML()
        yaml_obj.representer.add_representer(type(None), self.__represent_none)
        yaml_obj.default_flow_style = None
        yaml_obj.width = 120
        yaml_obj.representer.ignore_aliases = lambda *args: True
        return yaml_obj

    def __represent_none(self, yaml_obj, data):
        """YAML representation for `None`"""
        return yaml_obj.represent_scalar("tag:yaml.org,2002:null", "~")
