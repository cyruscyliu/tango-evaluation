#!/bin/bash

target=$1

if [ -z ${target} ]; then
    echo "target is missing"
    echo "usage: $0 target"
    exit 1
fi

if [ ${target} == 'forked-daapd' ]; then
    working_dir=specs/daap
elif [ ${target} == 'tinydtls' ]; then
    working_dir=specs/dtls
elif [ ${target} == 'bftpd' ]; then
    working_dir=specs/ftp
elif [ ${target} == 'proftpd' ]; then
    working_dir=specs/ftp
elif [ ${target} == 'live555' ]; then
    working_dir=specs/rtsp
elif [ ${target} == 'openssl' ]; then
    working_dir=specs/tls
elif [ ${target} == 'dcmtk' ]; then
    working_dir=specs/dicom
elif [ ${target} == 'kamailio' ]; then
    working_dir=specs/sip
elif [ ${target} == 'lightftp' ]; then
    working_dir=specs/ftp
elif [ ${target} == 'pureftpd' ]; then
    working_dir=specs/ftp
elif [ ${target} == 'dnsmasq' ]; then
    working_dir=specs/dns
elif [ ${target} == 'openssh' ]; then
    working_dir=specs/ssh
elif [ ${target} == 'exim' ]; then
    working_dir=specs/smtp
else
    echo "usage: $0 target"
    exit 1
fi

rm -rf pcaps_to_replay/${target} && mkdir -p pcaps_to_replay/${target}
dest_dir=$(realpath ./pcaps_to_replay/${target})

# let's go
for run in $(seq 0 4); do
    aflnet=$(realpath pfb-eval-afl-24h/out-${target}-aflnet-00${run}/replayable-queue)
    aflpp=$(realpath pfb-eval-afl-24h/out-${target}-aflpp-00${run}/default/queue)
    aflnet_no_state=$(realpath pfb-eval-afl-24h/out-${target}-aflnet-no-state-00${run}/replayable-queue)
    nyx=$(realpath pfb-eval-nyx-24h/out-${target}-00${run}/corpus/normal)
    nyx_aggressive=$(realpath pfb-eval-nyx-24h/out-${target}-aggressive-00${run}/corpus/normal)
    nyx_balanced=$(realpath pfb-eval-nyx-24h/out-${target}-00${run}/corpus/normal)

    pushd ${working_dir}

    mkdir -p ${dest_dir}/out-${target}-aflnet-00${run}
    python3.11 nyx_net_spec.py aflnet ${aflnet} ${dest_dir}/out-${target}-aflnet-00${run}
    mkdir -p ${dest_dir}/out-${target}-aflpp-00${run}
    python3.11 nyx_net_spec.py aflpp ${aflpp} ${dest_dir}/out-${target}-aflpp-00${run}
    mkdir -p ${dest_dir}/out-${target}-aflnet_no_state-00${run}
    python3.11 nyx_net_spec.py aflnet ${aflnet_no_state} ${dest_dir}/out-${target}-aflnet_no_state-00${run}
    mkdir -p ${dest_dir}/out-${target}-nyx-00${run}
    echo python3.11 nyx_net_spec.py ${nyx} ${dest_dir}/out-${target}-nyx-00${run}
    mkdir -p ${dest_dir}/out-${target}-nyx_aggressive-00${run}
    echo python3.11 nyx_net_spec.py ${nyx_aggressive} ${dest_dir}/out-${target}-nyx_aggressive-00${run}
    mkdir -p ${dest_dir}/out-${target}-nyx_balanced-00${run}
    echo python3.11 nyx_net_spec.py ${nyx_balanced} ${dest_dir}/out-${target}-nyx_balanced-00${run}

    popd
done
