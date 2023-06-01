#!/bin/bash

target=$1

if [ -z ${target} ]; then
    echo "target is missing"
    echo "usage: $0 target"
    exit 1
fi

if [ ${target} == 'live555' ]; then
    working_dir=specs/rtsp
elif [ ${target} == 'openssl' ]; then
    working_dir=specs/tls
else
    echo "usage: $0 target"
    exit 1
fi

dest_dir=$(realpath ./pcaps_to_replay/${target})

# let's go
for run in $(seq 0 4); do
    sgfuzz=$(realpath pfb-eval-sgfuzz-24h/out-sgfuzz-${target}-00${run})

    pushd ${working_dir}
    rm -rf ${dest_dir}/out-${target}-sgfuzz-00${run}
    mkdir -p ${dest_dir}/out-${target}-sgfuzz-00${run}/queue
    # raw bytes like aflpp
    python3.11 nyx_net_spec.py aflpp ${sgfuzz} ${dest_dir}/out-${target}-sgfuzz-00${run}/queue

    popd
done
