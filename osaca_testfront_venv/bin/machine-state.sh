#!/bin/bash -l

### Configurations ####
DO_LIKWID=1
LIKWID_PATH=""
DMIDECODE_FILE=/etc/dmidecode.txt
#######################

function header {
    echo
    echo "################################################################################"
    echo "# $1"
    echo "################################################################################"
}

function likwid_command_exists {
    if [[ -z "${LIKWID_PATH//}" ]]; then
        checkCmd=$(command -v $1)
    else
        checkCmd=$(command -v $LIKWID_PATH"/""$1")
    fi
    if [ ${DO_LIKWID} ]; then
        if [[ -z "${checkCmd//}" ]]; then
            echo "false"
        else
            echo "true"
        fi
    else
        echo "false"
    fi
}

function likwid_command {
    if [ ${DO_LIKWID} ]; then
        if [[ -z "${LIKWID_PATH//}" ]]; then
            command $1
        else
            command "$LIKWID_PATH""/""$1"
        fi
    fi
}


function print_powercap_folder {
    FOLDER=$1
    if [ -e $FOLDER/name ]; then
        NAME=$(cat $FOLDER/name)
        echo "RAPL domain ${NAME}"
    else
        return
    fi
    if [ -e $FOLDER/constraint_0_name ]; then
        LIMIT0_NAME=$(cat $FOLDER/constraint_0_name)
        if [ -e $FOLDER/constraint_0_power_limit_uw ]; then
            LIMIT0_LIMIT=$(cat $FOLDER/constraint_0_power_limit_uw 2>/dev/null)
            if [ -z "$LIMIT0_LIMIT" ]; then LIMIT0_LIMIT="NA"; fi
        else
            LIMIT0_LIMIT="NA"
        fi
        if [ -e $FOLDER/constraint_0_max_power_uw ]; then
            LIMIT0_MAXPOWER=$(cat $FOLDER/constraint_0_max_power_uw 2>/dev/null)
            if [ -z "$LIMIT0_MAXPOWER" ]; then LIMIT0_MAXPOWER="NA"; fi
        else
            LIMIT0_MAXPOWER="NA"
        fi
        if [ -e $FOLDER/constraint_0_time_window_us ]; then
            LIMIT0_TIMEWIN=$(cat $FOLDER/constraint_0_time_window_us 2>/dev/null)
            if [ -z "$LIMIT0_TIMEWIN" ]; then LIMIT0_TIMEWIN="NA"; fi
        else
            LIMIT0_TIMEWIN="NA"
        fi
        echo "- Limit0 ${LIMIT0_NAME} MaxPower ${LIMIT0_MAXPOWER}uW Limit ${LIMIT0_LIMIT}uW TimeWindow ${LIMIT0_TIMEWIN}us"
    fi
    if [ -e $FOLDER/constraint_1_name ]; then
        LIMIT1_NAME=$(cat $FOLDER/constraint_1_name)
        if [ -e $FOLDER/constraint_1_power_limit_uw ]; then
            LIMIT1_LIMIT=$(cat $FOLDER/constraint_1_power_limit_uw 2>/dev/null)
            if [ -z "$LIMIT1_LIMIT" ]; then LIMIT1_LIMIT="NA"; fi
        else
            LIMIT1_LIMIT="NA"
        fi
        if [ -e $FOLDER/constraint_0_max_power_uw ]; then
            LIMIT1_MAXPOWER=$(cat $FOLDER/constraint_1_max_power_uw 2>/dev/null)
            if [ -z "$LIMIT1_MAXPOWER" ]; then LIMIT1_MAXPOWER="NA"; fi
        else
            LIMIT1_MAXPOWER="NA"
        fi
        if [ -e $FOLDER/constraint_0_time_window_us ]; then
            LIMIT1_TIMEWIN=$(cat $FOLDER/constraint_1_time_window_us 2>/dev/null)
            if [ -z "$LIMIT1_TIMEWIN" ]; then LIMIT1_TIMEWIN="NA"; fi
        else
            LIMIT1_TIMEWIN="NA"
        fi
        echo "- Limit1 ${LIMIT1_NAME} MaxPower ${LIMIT1_MAXPOWER}uW Limit ${LIMIT1_LIMIT}uW TimeWindow ${LIMIT1_TIMEWIN}us"
    fi
}

function print_frequencies {
    TPATH=/sys/devices/system/cpu
    for FOLDER in $TPATH/cpu[[:digit:]+]; do
        CPU=CPU$(basename "$FOLDER" | tr -d 'cpu' )
        CUR=$(cat $FOLDER/cpufreq/scaling_cur_freq)
        MIN=$(cat $FOLDER/cpufreq/scaling_min_freq)
        MAX=$(cat $FOLDER/cpufreq/scaling_max_freq)
        GOV=$(cat $FOLDER/cpufreq/scaling_governor)
        if [ $(cat $FOLDER/cpufreq/scaling_driver) == "intel_pstate" ]; then
            TURBO=$(expr $(cat $TPATH/intel_pstate/no_turbo) == 0)
        fi
        echo "$CPU $GOV $MIN kHz/$CUR kHz/$MAX kHz $TURBO"
    done
}

function check_dmidecode {
    AVAIL=$(which dmidecode)
    EXECUTABLE=$(dmidecode 2>&1 1>/dev/null || echo $?)
    if [ "$EXECUTABLE" == "0" ]; then
        dmidecode
    else
        if [ -e "$DMIDECODE_FILE" ]; then
            cat "$DMIDECODE_FILE"
        else
            echo "dmidecode not executable, so ask your administrator to put the"
            echo "dmidecode output to a file (configured $DMIDECODE_FILE)"
        fi
    fi
}

if [[ -z "${LIKWID_PATH//}" ]]; then
    if [ $(which likwid-topology 2>/dev/null | wc -l) != "1" ]; then
        module load likwid
        if [ $(which likwid-topology 2>/dev/null | wc -l) != "1" ]; then
            DO_LIKWID=0
        fi
    fi
else
        if [ $($LIKWID_PATH/likwid-topology 2>/dev/null | wc -l) != "1" ]; then
            echo "LIKWID not found in path"
            DO_LIKWID=0
        fi
fi


header "Hostname"
hostname -f
header "Operating System"
cat /etc/*release*
header "Operating System (LSB)"
if [ $(which lsb_release 2>/dev/null | wc -l) > 0 ]; then
    lsb_release 2>&1
fi
header "Operating System Kernel"
uname -a


header "Logged in users"
users
w

if [ $(likwid_command_exists likwid-pin) = "true" ]; then
    header "CPUset"
    likwid_command "likwid-pin -p"
fi

header "CGroups"
echo -n "Allowed CPUs: "
cat /sys/fs/cgroup/cpuset/cpuset.effective_cpus
echo -n "Allowed Memory controllers: "
cat /sys/fs/cgroup/cpuset/cpuset.effective_mems

header "Topology"
if [ $(likwid_command_exists likwid-topology) = "true" ]; then
    likwid_command "likwid-topology"
else
    lscpu
fi
if [ $(which numactl 2>/dev/null | wc -l ) == 1 ]; then
    header "NUMA Topology"
    numactl -H
fi

header "Frequencies"
if [ $(likwid_command_exists likwid-setFrequencies) = "true" ]; then
    likwid_command "likwid-setFrequencies -p"
else
    print_frequencies
fi

header "Prefetchers"
if [ $(likwid_command_exists likwid-features) = "true" ]; then
    likwid_command "likwid-features -l -c N"
else
    echo "likwid-features not available"
fi

header "Load"
cat /proc/loadavg

if [ $(likwid_command_exists "likwid-powermeter") ]; then
    header "Performance energy bias"
    likwid_command "likwid-powermeter -i" | grep -i bias
fi

header "NUMA balancing"
echo -n "Enabled: "
cat /proc/sys/kernel/numa_balancing

header "General memory info"
cat /proc/meminfo

header "Transparent huge pages"
echo -n "Enabled: "
cat /sys/kernel/mm/transparent_hugepage/enabled
echo -n "Use zero page: "
cat /sys/kernel/mm/transparent_hugepage/use_zero_page

header "Hardware power limits"
RAPL_FOLDERS=$(find /sys/devices/virtual/powercap -name "intel-rapl\:*")
for F in ${RAPL_FOLDERS}; do print_powercap_folder $F; done



OUT=$(module 2>&1 1>/dev/null || echo $?)
if [ "$OUT" == "0" ]; then
    header "Modules"
    module list 2>&1
fi

header "Compiler"
CC=""
if [ $(which icc 2>/dev/null | wc -l ) == 1 ]; then
    CC=$(which icc)
elif [ $(which gcc 2>/dev/null | wc -l ) == 1 ]; then
    CC=$(which gcc)
elif [ $(which clang 2>/dev/null | wc -l ) == 1 ]; then
    CC=$(which clang)
fi
$CC --version

header "MPI"
if [ $(which mpiexec 2>/dev/null | wc -l ) == 1 ]; then
    mpiexec --version
elif [ $(which mpiexec.hydra 2>/dev/null | wc -l ) == 1 ]; then
    mpiexec.hydra --version
elif [ $(which mpirun 2>/dev/null | wc -l ) == 1 ]; then
    mpirun --version
else
    echo "No MPI found"
fi


if [ $(which nvidia-smi 2>/dev/null | wc -l ) == 1 ]; then
    header "Nvidia GPUs"
    nvidia-smi
fi

if [ $(which veosinfo 2>/dev/null | wc -l ) == 1 ]; then
    header "NEC Tsubasa"
    veosinfo
fi

header "dmidecode"
check_dmidecode

header "environment variables"
env

if [ $# -ge 1 ]; then
    header "Executable"
    echo -n "Name: "
    echo $1
    if [ $($1 --version 2>/dev/null | wc -l) -gt 0 ]; then
        echo -n "Version: "
        $1 --version
    fi
    if [ $(which $1 2>/dev/null | wc -l ) == 1 ]; then
        echo "Libraries:"
        ldd $(which $1)
    fi
fi

