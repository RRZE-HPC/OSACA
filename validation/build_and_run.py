#!/usr/bin/env python3
import sys
import os
import re
from subprocess import check_call, check_output, CalledProcessError, STDOUT
from itertools import chain
import shutil
from functools import lru_cache
from glob import glob
from pathlib import Path
from pprint import pprint
import socket
import pickle

import numpy as np
import pandas as pd

from kerncraft.models import benchmark
from kerncraft.incore_model import (
    asm_instrumentation,
    iaca_analyse_instrumented_binary,
    osaca_analyse_instrumented_assembly,
    llvm_mca_analyse_instrumented_assembly
)


# Scaling of inner dimension for 1D, 2D and 3D kernels
#  * consider kernels to be compiled with multiple compilers and different options
#  * find best performing run (min cy/it over all runs)
#  * statistics on performance overall (cy/it over inner length)
#  * validate that L2 traffic is neglegible
#  * measure other performance metrics, such as port utilization (optionally)
#  * scale to highlevel iterations
# Collect inner loop body assembly for each kernel/compiler/options combination
#  * analyze with OSACA, IACA and LLVM-MCA

hosts_arch_map = {r"skylakesp2": "SKX",
                  r"ivyep1": "IVB",
                  r"naples1": "ZEN",
                  r"rome1": "ZEN2",
                  r"warmup": "TX2",
                  r"qp4-node-[0-9]+": "A64FX"}

arch_info = {
    'SKX': {
        'IACA': 'SKX',
        'OSACA': 'SKX',
        'LLVM-MCA': '-mcpu=skylake-avx512',
        'isa': 'x86',
        'perfevents': [],
        "cflags": {
            'icc': {
                "Ofast": "-Ofast -fno-alias -xCORE-AVX512 -qopt-zmm-usage=high -nolib-inline -ffreestanding".split(),
                "O3": "-O3 -fno-alias -xCORE-AVX512 -qopt-zmm-usage=high -nolib-inline -ffreestanding".split(),
                "O2": "-O2 -fno-alias -xCORE-AVX512 -qopt-zmm-usage=high -nolib-inline -ffreestanding".split(),
                "O1": "-O1 -fno-alias -xCORE-AVX512 -qopt-zmm-usage=high -nolib-inline -ffreestanding".split(),
            },
            'clang': {
                "Ofast": "-Ofast -march=skylake-avx512 -ffreestanding".split(),
                "O3": "-O3 -march=skylake-avx512 -ffreestanding".split(),
                "O2": "-O2 -march=skylake-avx512 -ffreestanding".split(),
                "O1": "-O1 -march=skylake-avx512 -ffreestanding".split(),
                
            },
            'gcc': {
                "Ofast": "-Ofast -march=skylake-avx512 -lm -ffreestanding".split(),
                "O3": "-O3 -march=skylake-avx512 -lm -ffreestanding".split(),
                "O2": "-O2 -march=skylake-avx512 -lm -ffreestanding".split(),
                "O1": "-O1 -march=skylake-avx512 -lm -ffreestanding".split(),
            },
        },
    },
    'IVB': {
        'IACA': 'IVB',
        'OSACA': 'IVB',
        'LLVM-MCA': '-mcpu=ivybridge',
        'isa': 'x86',
        'perfevents': [],
        "cflags": {
            "icc": {
                "Ofast": "-Ofast -xAVX -fno-alias -nolib-inline -ffreestanding".split(),
                "O3": "-O3 -xAVX -fno-alias -nolib-inline -ffreestanding".split(),
                "O2": "-O2 -xAVX -fno-alias -nolib-inline -ffreestanding".split(),
                "O1": "-O1 -xAVX -fno-alias -nolib-inline -ffreestanding".split(),
            },
            "clang": {
                "Ofast": "-Ofast -mavx -ffreestanding".split(),
                "O3": "-O3 -mavx -ffreestanding".split(),
                "O2": "-O2 -mavx -ffreestanding".split(),
                "O1": "-O1 -mavx -ffreestanding".split(),
            },
            "gcc": {
                "Ofast": "-Ofast -march=corei7-avx -lm -ffreestanding".split(),
                "O3": "-O3 -march=corei7-avx -lm -ffreestanding".split(),
                "O2": "-O2 -march=corei7-avx -lm -ffreestanding".split(),
                "O1": "-O1 -march=corei7-avx -lm -ffreestanding".split(),
            },
        },
    },
    'ZEN': {
        'IACA': None,
        'OSACA': 'ZEN1',
        'LLVM-MCA': '-mcpu=znver1',
        'isa': 'x86',
        'perfevents': [],
        "cflags": {
            "clang": {
                "Ofast": "-Ofast -march=znver1 -ffreestanding".split(),
                "O3": "-O3 -march=znver1 -ffreestanding".split(),
                "O2": "-O2 -march=znver1 -ffreestanding".split(),
                "O1": "-O1 -march=znver1 -ffreestanding".split(),
            },
            "gcc": {
                "Ofast": "-Ofast -march=znver1 -ffreestanding".split(),
                "O3": "-O3 -march=znver1 -ffreestanding".split(),
                "O2": "-O2 -march=znver1 -ffreestanding".split(),
                "O1": "-O1 -march=znver1 -ffreestanding".split(),
            },
            "icc": {
                "Ofast": "-Ofast -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
                "O3": "-O3 -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
                "O2": "-O2 -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
                "O1": "-O1 -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
            },
        },
    },
    'ZEN2': {
        'IACA': None,
        'OSACA': 'ZEN2',
        'LLVM-MCA': '-mcpu=znver2',
        'isa': 'x86',
        'perfevents': [],
        "cflags": {
            "clang": {
                "Ofast": "-Ofast -march=znver2 -ffreestanding".split(),
                "O3": "-O3 -march=znver2 -ffreestanding".split(),
                "O2": "-O2 -march=znver2 -ffreestanding".split(),
                "O1": "-O1 -march=znver2 -ffreestanding".split(),
            },
            "gcc": {
                "Ofast": "-Ofast -march=znver2 -ffreestanding".split(),
                "O3": "-O3 -march=znver2 -ffreestanding".split(),
                "O2": "-O2 -march=znver2 -ffreestanding".split(),
                "O1": "-O1 -march=znver2 -ffreestanding".split(),
            },
            "icc": {
                "Ofast": "-Ofast -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
                "O3": "-O3 -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
                "O2": "-O2 -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
                "O1": "-O1 -xAVX2 -fno-alias -nolib-inline -ffreestanding".split(),
            },
        },
    },
    'TX2': {
        'IACA': None,
        'OSACA': 'TX2',
        'LLVM-MCA': '-mcpu=thunderx2t99 -march=aarch64',
        'isa': 'aarch64',
        'perfevents': [],
        "cflags": {
            "clang": {
                "Ofast": "-Ofast -target aarch64-unknown-linux-gnu -ffreestanding".split(),
                "O3": "-O3 -target aarch64-unknown-linux-gnu -ffreestanding".split(),
                "O2": "-O2 -target aarch64-unknown-linux-gnu -ffreestanding".split(),
                "O1": "-O1 -target aarch64-unknown-linux-gnu -ffreestanding".split(),
            },
            "gcc": {
                "Ofast": "-Ofast -march=armv8.1-a -ffreestanding".split(),
                "O3": "-O3 -march=armv8.1-a -ffreestanding".split(),
                "O2": "-O2 -march=armv8.1-a -ffreestanding".split(),
                "O1": "-O1 -march=armv8.1-a -ffreestanding".split(),
            },
        },
    },
    'A64FX': {
        'Clock [MHz]': 1800,  # reading out via perf. counters is not supported
        'L2_volume_metric': 'L1<->L2 data volume [GBytes]',
        'IACA': None,
        'OSACA': 'A64FX',
        'LLVM-MCA': '-mcpu=a64fx -march=aarch64',
        'isa': 'aarch64',
        'perfevents': [],
        "cflags": {
            "gcc": {
                "Ofast": "-Ofast -msve-vector-bits=512 -march=armv8.2-a+sve -ffreestanding".split(),
                "O3": "-O3 -msve-vector-bits=512 -march=armv8.2-a+sve -ffreestanding".split(),
                "O2": "-O2 -msve-vector-bits=512 -march=armv8.2-a+sve -ffreestanding".split(),
                "O1": "-O1 -msve-vector-bits=512 -march=armv8.2-a+sve -ffreestanding".split(),
            },
            "clang": {
                "Ofast": "-Ofast -target aarch64-unknown-linux-gnu -ffreestanding".split(),
                "O3": "-O3 -target aarch64-unknown-linux-gnu -ffreestanding".split(),
                "O2": "-O2 -target aarch64-unknown-linux-gnu -ffreestanding".split(),
                "O1": "-O1 -target aarch64-unknown-linux-gnu -ffreestanding".split(),
            },
        }
    },
}


def get_current_arch():
    hostname = socket.gethostname()
    if hostname in hosts_arch_map:
        return hosts_arch_map[hostname]
    for matchstr, arch in hosts_arch_map.items():
        if re.match(matchstr, hostname):
            return arch
    # raise KeyError(f"{hostname} not matched in hosts_arch_map.")
    return None


def get_kernels(kernels=None):
    if kernels is None:
        kernels = []
        for f in glob("kernels/*.c"):
            f = f.rsplit('.', 1)[0].split('/', 1)[1]
            if f == "dummy":
                continue
            kernels.append(f)
    return kernels

# Columns:
# arch
# kernel
# compiler
# cflags_name
# element_size
# pointer_increment
# IACA_raw
# IACA_scaled [dict with cy/it]
# IACA_scaled_max [float with cy/it]
# OSACA_raw
# OSACA_scaled [dict with cy/it]
# OSACA_scaled_max [float with cy/it]
# LLVM-MCA_raw
# LLVM-MCA_scaled [dict with cy/it]
# LLVM-MCA_scaled_max [float with cy/it]
# best_length
# best_runtime [cy/it]
# L2_traffic [B/it]
# allruns [list (length, repetitions, cy/it, L2 B/it)]
# perfevents [dict event: counter/it]

def build_mark_run_all_kernels(measurements=True, osaca=True, iaca=True, llvm_mca=True):
    arch = get_current_arch()
    if arch is None:
        arches = arch_info.keys()
        islocal = False
    else:
        arches = [arch]
        islocal = True
    for arch in arches:
        ainfo = arch_info.get(arch)
        print(arch)
        data_path = Path(f"build/{arch}/data.pkl")
        if data_path.exists():
            with data_path.open('rb') as f:
                data = pickle.load(f)
        else:
            data = []
        for compiler, compiler_cflags in ainfo['cflags'].items():
            if not shutil.which(compiler) and islocal:
                print(compiler, "not found in path! Skipping...")
                continue
            for cflags_name, cflags in compiler_cflags.items():
                for kernel in get_kernels():
                    print(f"{kernel:<15} {arch:>5} {compiler:>5} {cflags_name:>6}",
                        end=": ", flush=True)
                    row = list([r for r in data
                                if r['arch'] == arch and r['kernel'] == kernel and
                                r['compiler'] == compiler and r['cflags_name'] == cflags_name])
                    if row:
                        row = row[0]
                    else:
                        row = {
                            'arch': arch,
                            'kernel': kernel,
                            'compiler': compiler,
                            'cflags_name': cflags_name,
                            'element_size': 8,
                        }
                        data.append(row)

                    # Build
                    print("build", end="", flush=True)
                    asm_path, exec_path, overwrite = build_kernel(
                        kernel, arch, compiler, cflags, cflags_name, dontbuild=islocal)

                    # Mark for IACA, OSACA and LLVM-MCA
                    print("mark", end="", flush=True)
                    try:
                        marked_asmfile, marked_objfile, row['pointer_increment'] = mark(
                            asm_path, compiler, cflags, isa=ainfo['isa'], overwrite=overwrite)
                    except ValueError as e:
                        row['marking_error'] = str(e)
                        print(":", e)
                        continue

                    # Analyze with IACA, if requested and configured
                    if iaca and ainfo['IACA'] is not None:
                        print("IACA", end="", flush=True)
                        if not row.get('IACA_ports') or overwrite:
                            row['IACA_raw'] = iaca_analyse_instrumented_binary(
                                marked_objfile, micro_architecture=ainfo['IACA'])
                            row['IACA_ports'] = \
                                {k: v/(row['pointer_increment']/row['element_size'])
                                for k,v in row['IACA_raw']['port cycles'].items()}
                            row['IACA_prediction'] = row['IACA_raw']['throughput']/(
                                row['pointer_increment']/row['element_size'])
                            row['IACA_throughput'] = max(row['IACA_ports'].values())
                            print(". ", end="", flush=True)
                        else:
                            print("! ", end="", flush=True)

                    # Analyze with OSACA, if requested
                    if osaca:
                        print("OSACA", end="", flush=True)
                        if ainfo['OSACA'] is not None and (not row.get('OSACA_ports') or overwrite):
                            row['OSACA_raw'] = osaca_analyse_instrumented_assembly(
                                marked_asmfile, micro_architecture=ainfo['OSACA'])
                            row['OSACA_ports'] = \
                                {k: v/(row['pointer_increment']/row['element_size'])
                                for k,v in row['OSACA_raw']['port cycles'].items()}
                            row['OSACA_prediction'] = row['OSACA_raw']['throughput']/(
                                row['pointer_increment']/row['element_size'])
                            row['OSACA_throughput'] = max(row['OSACA_ports'].values())
                            row['OSACA_cp'] = row['OSACA_raw']['cp_latency']
                            row['OSACA_lcd'] = row['OSACA_raw']['lcd']
                            print(". ", end="", flush=True)
                        else:
                            print("! ", end="", flush=True)

                    # Analyze with LLVM-MCA, if requested and configured
                    if llvm_mca and ainfo['LLVM-MCA'] is not None:
                        print("LLVM-MCA", end="", flush=True)
                        if not row.get('LLVM-MCA_ports') or overwrite:
                            row['LLVM-MCA_raw'] = llvm_mca_analyse_instrumented_assembly(
                                marked_asmfile,
                                micro_architecture=ainfo['LLVM-MCA'],
                                isa=ainfo['isa'])
                            row['LLVM-MCA_ports'] = \
                                {k: v/(row['pointer_increment']/row['element_size'])
                                for k,v in row['LLVM-MCA_raw']['port cycles'].items()}
                            row['LLVM-MCA_prediction'] =row['LLVM-MCA_raw']['throughput']/(
                                row['pointer_increment']/row['element_size'])
                            row['LLVM-MCA_throughput'] = max(row['LLVM-MCA_ports'].values())
                            row['LLVM-MCA_cp'] = row['LLVM-MCA_raw']['cp_latency']
                            row['LLVM-MCA_lcd'] = row['LLVM-MCA_raw']['lcd']
                            print(". ", end="", flush=True)
                        else:
                            print("! ", end="", flush=True)

                    if measurements and islocal:
                        # run measurements if on same hardware
                        print("scale", end="", flush=True)
                        if not row.get('best_length') or overwrite:
                            # find best length with concurrent L2 measurement
                            scaling_runs, best = scalingrun(exec_path)
                            row['best_length'] = best[0]
                            row['best_runtime'] = best[2]
                            row['L2_traffic'] = best[3]
                            row['allruns'] = scaling_runs
                            print(f"({best[0]}). ", end="", flush=True)
                        else:
                            print(f"({row.get('best_length', None)})! ", end="", flush=True)

                        # TODO measure all events on best length
                        print("perf", end="", flush=True)
                        if not row.get('perfevents') or overwrite:
                            print("???", end="", flush=True)
                        else:
                            print("! ", end="", flush=True)

                    print()
                    # dump to file
                    with data_path.open('wb') as f:
                        try:
                            pickle.dump(data, f)
                        except KeyboardInterrupt:
                            f.seek(0)
                            pickle.dump(data, f)
                            sys.exit()
                        


def scalingrun(kernel_exec, total_iterations=25000000, lengths=range(8, 4*1024+1)):
    #print('{:>8} {:>10} {:>10}'.format("x", "cy/it", "L2 B/it"))
    parameters = chain(*[[total_iterations//i, i] for i in lengths])
    # TODO use arch specific events and grooup
    r, o = perfctr(chain([kernel_exec], map(str, parameters)),
                1, group="L2")
    global_infos = {}
    for m in [re.match(r"(:?([a-z_\-0-9]+):)?([a-z]+): ([a-z\_\-0-9]+)", l) for l in o]:
        if m is not None:
            try:
                v = int(m.group(4))
            except ValueError:
                v = m.group(4)
            if m.group(1) is None:
                global_infos[m.group(3)] = v
            else:
                r[m.group(2)][m.group(3)] = v

    results = []
    best = (float('inf'), None)
    for markername, mmetrics in r.items():
        kernelname, repetitions, *_, xlength = markername.split('_')
        repetitions = int(repetitions)
        xlength = int(xlength)
        total_iterations = mmetrics['repetitions'] * mmetrics['iterations']
        if 'Clock [MHz]' in mmetrics:
            clock_hz = mmetrics['Clock [MHz]']*1e6
        else:
            clock_hz = arch_info[get_current_arch()]['Clock [MHz]']*1e6
        cyperit = mmetrics['Runtime (RDTSC) [s]'] * clock_hz / total_iterations
        # TODO use arch specific events and grooup
        if 'L2D loaad data volume [GBytes]' in mmetrics:
            l2perit = (mmetrics['L2D load data volume [GBytes]'] +
                       mmetrics.get('L2D evict data volume [GBytes]', 0))*1e9 / total_iterations
        else:
            l2perit = \
                mmetrics[arch_info[get_current_arch()]['L2_volume_metric']]*1e9 / total_iterations
        results.append(
            (xlength, repetitions, cyperit, l2perit)
        )
        if cyperit < best[0]:
            best = cyperit, results[-1]
    return results, best[1]

def mark(asm_path, compiler, cflags, isa, overwrite=False):
    # Mark assembly for IACA, OSACA and LLVM-MCA
    marked_asm_path = Path(asm_path).with_suffix(".marked.s")
    if not marked_asm_path.exists() or overwrite:
        with open(asm_path) as fa, open(marked_asm_path, 'w') as fm:
            try:
                _, pointer_increment = asm_instrumentation(fa, fm, isa=isa)
            except KeyboardInterrupt:
                fm.close()
                marked_asm_path.unlink()
        print(". ", end="", flush=True)
    else:
        # use maked assembly and extract asm_block and pointer_increment
        with open(marked_asm_path) as f:
            marked_asm = f.read()
        m = re.search(r'pointer_increment=([0-9]+)', marked_asm)
        if m:
            pointer_increment = int(m.group(1))
        else:
            os.unlink(marked_asm_path)
            raise ValueError(
                "Could not find `pointer_increment=<byte increment>`. Plase place into file.")
        print("! ", end="", flush=True)

    # Compile marked assembly to object for IACA
    marked_obj = Path(asm_path).with_suffix(".marked.o")
    if not marked_obj.exists():
        check_call([compiler] + ['-c', str(marked_asm_path), '-o', str(marked_obj)])
    
    return str(marked_asm_path), str(marked_obj), pointer_increment


def build_kernel(kernel, architecture, compiler, cflags, cflags_name, overwrite=False,
                 dontbuild=False):
    build_path = f"build/{architecture}/{compiler}/{cflags_name}"
    kernel_assembly = f"{build_path}/{kernel}.s"
    kernel_object= f"{build_path}/{kernel}.o"
    executable = f"{build_path}/{kernel}"
    Path(build_path).mkdir(parents=True, exist_ok=True)

    if not overwrite:
        # Overwrite if any kernel specific file is missing
        overwrite = (
            not os.path.exists(kernel_object) or 
            not os.path.exists(kernel_assembly) or
            not os.path.exists(executable))

    if dontbuild and overwrite:
        raise ValueError("Must build, but not allowed.")

    if not Path(f"{build_path}/dummy.o").exists():
        check_call([compiler] + cflags + ["-c", "kernels/dummy.c", "-o", f"{build_path}/dummy.o"])

    if not Path(f"{build_path}/compiler_version").exists():
        # Document compiler version
        with open(f"{build_path}/compiler_version", 'w') as f:
            f.write(check_output([compiler, "-v"], encoding='utf8', stderr=STDOUT))

    if overwrite:
        # build object + assembly
        check_call([compiler] +
                   cflags +
                   ["-c", f"kernels/{kernel}.c", "-o", kernel_object])
        check_call([compiler] +
                   cflags +
                   ["-c", f"kernels/{kernel}.c", "-S", "-o", kernel_assembly])

        # build main and link executable
        executable_cflags = [
            os.environ["LIKWID_DEFINES"],
            os.environ["LIKWID_INC"],
            os.environ["LIKWID_LIB"]
        ] + ['-Ofast']
        check_call([compiler] + executable_cflags + [
            f"{build_path}/dummy.o",
            kernel_object,
            "-DMAIN",
            f"kernels/{kernel}.c",
            "-llikwid",
            "-o", executable])
        print(". ", end="", flush=True)
    else:
        print("! ", end="", flush=True)
    
    return kernel_assembly, executable, overwrite


def perfctr(cmd, cores, group='MEM', code_markers=True, verbose=0):
    """
    Run *cmd* with likwid-perfctr and returns result as dict.

    *group* may be a performance group known to likwid-perfctr or an event string.

    if CLI argument cores > 1, running with multi-core, otherwise single-core
    """
    # Making sure likwid-perfctr is available:
    if benchmark.find_executable('likwid-perfctr') is None:
        print("likwid-perfctr was not found. Make sure likwid is installed and found in PATH.",
                file=sys.stderr)
        sys.exit(1)

    # FIXME currently only single core measurements support!
    perf_cmd = ['likwid-perfctr', '-f', '-O', '-g', group]

    cpu = 'S0:0'
    if cores > 1:
        cpu += '-'+str(cores-1)

    # Pinned and measured on cpu
    perf_cmd += ['-C', cpu]

    # code must be marked using likwid markers
    perf_cmd.append('-m')

    perf_cmd += cmd
    if verbose > 1:
        print(' '.join(perf_cmd))
    try:
        with benchmark.fix_env_variable('OMP_NUM_THREADS', None):
            output = check_output(perf_cmd).decode('utf-8').split('\n')
    except CalledProcessError as e:
        print("Executing benchmark failed: {!s}".format(e), file=sys.stderr)
        sys.exit(1)

    # TODO multicore output is different and needs to be considered here!
    results = {}
    cur_region_name = None
    cur_region_data = {}
    for line in output:
        if line == "STRUCT,Info,3" and cur_region_name is not None:
            results[cur_region_name] = cur_region_data
            cur_region_name = None
            cur_region_data = {}
        m = re.match(r"TABLE,Region ([a-z\-0-9_]+),", line)
        if m:
            cur_region_name = m.group(1)
        line = line.split(',')
        try:
            # Metrics
            cur_region_data[line[0]] = float(line[1])
            continue
        except ValueError:
            # Would not convert to float
            pass
        except IndexError:
            # Not a parable line (did not contain any commas)
            continue
        try:
            # Event counters
            if line[2] == '-' or line[2] == 'nan':
                counter_value = 0
            else:
                counter_value = int(line[2])
            if re.fullmatch(r'[A-Z0-9_]+', line[0]) and \
                    re.fullmatch(r'[A-Z0-9]+(:[A-Z0-9]+=[0-9A-Fa-fx]+)*', line[1]):
                cur_region_data.setdefault(line[0], {})
                cur_region_data[line[0]][line[1]] = counter_value
                continue
        except (IndexError, ValueError):
            pass
        if line[0].endswith(":") and len(line) == 3 and line[2] == "":
            # CPU information strings
            cur_region_data[line[0]] = line[1]
            continue
    results[cur_region_name] = cur_region_data
    return results, output


def main():
    # Build and mark all kernels (that can be build)
    #for r in zip(*[scalingrun('build/SKX/icc/Ofast/3d-r3-11pt') for i in range(10)]):
    #    print("\n".join(["{} {} {} {:.2f} {:.2f}".format(*e) for e in r]))
    #    print()
    
    # Check for correct LLVM-MCA version
    try:
        llvm_mca = 'LLVM version 12.0.0' in check_output(['llvm-mca', '-version']).decode()
    except FileNotFoundError:
        llvm_mca = False
    
    build_mark_run_all_kernels(measurements='--no-measurements' not in sys.argv, llvm_mca=llvm_mca)
    sys.exit()

if __name__ == "__main__":
    main()