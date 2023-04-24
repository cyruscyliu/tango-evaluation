#!/bin/bash

target=$1
dir_of_raw_bytes=$2
dir_of_pcaps=$(basename $2).pcap

if [ -z ${target} ]; then
    echo "target is missing"
    echo "usage: $0 target dir_of_raw_bytes"
    exit 1
fi

if [ -z ${dir_of_raw_bytes} ]; then
    echo "dir_of_raw_bytes is missing"
    echo "usage: $0 target dir_of_raw_bytes"
    exit 1
fi

echo "converting raw bytes in ${dir_of_raw_bytes} to ${dir_of_pcaps}"

if [ ${target} == 'forked-daapd' ]; then
    script=specs/daapd/nyx_net_spec.py
elif [ ${target} == 'tinydtlS' ]; then
    script=specs/dtls/nyx_net_spec.py
elif [ ${target} == 'bftpd' ]; then
    script=specs/ftp/nyx_net_spec.py
elif [ ${target} == 'proftpd' ]; then
    script=specs/ftp/nyx_net_spec.py
elif [ ${target} == 'live555' ]; then
    script=specs/rtsp/nyx_net_spec.py
elif [ ${target} == 'openssl' ]; then
    script=specs/tls/nyx_net_spec.py
elif [ ${target} == 'dcmtk' ]; then
    script=specs/dicom/nyx_net_spec.py
elif [ ${target} == 'kamailio' ]; then
    script=specs/sip/nyx_net_spec.py
elif [ ${target} == 'lightftp' ]; then
    script=specs/ftp/nyx_net_spec.py
elif [ ${target} == 'pureftpd' ]; then
    script=specs/ftp/nyx_net_spec.py
elif [ ${target} == 'dnsmasq' ]; then
    script=specs/dns/nyx_net_spec.py
elif [ ${target} == 'openssh' ]; then
    script=specs/ssh/nyx_net_spec.py
elif [ ${target} == 'exim' ]; then
    script=specs/smtp/nyx_net_spec.py
else
    echo "usage: $0 target dir_of_raw_bytes"
    exit 1
fi

dest_dir=pcaps_to_replay
rm -rf $dest_dir && mkdir $dest_dir

# let's go
for run in $(seq 0 10); do
    aflnet=pfb-eval-afl-24h/out-${target}-aflnet-00${run}/queue
    aflpp=pfb-eval-afl-24h/out-${target}-aflpp-00${run}/default/queue
    aflnet_no_state=pfb-eval-afl-24h/out-${target}-aflnet-no-state-00${run}/queue
    nyx=pfb-eval-nyx-24h/out-${target}-00${run}/corpus/normal
    nyx_aggressive=pfb-eval-nyx-24h/out-${target}-aggressive-00${run}/corpus/normal
    nyx_balanced=pfb-eval-nyx-24h/out-dcmtk-${target}-00${run}/corpus/normal

    python ${script} ${aflnet} ${dest_dir}/out-${target}-aflnet-00${run}
    python ${script} ${aflpp} ${dest_dir}/out-${target}-aflpp-00${run}
    python ${script} ${aflnet_no_state} ${dest_dir}/out-${target}-aflnet_no_state-00${run}
    python ${script} ${nyx} ${dest_dir}/out-${target}-nyx-00${run}
    python ${script} ${nyx_aggressive} ${dest_dir}/out-${target}-nyx_aggressive-00${run}
    python ${script} ${nyx_balanced} ${dest_dir}/out-${target}-nyx_balanced-00${run}
done
