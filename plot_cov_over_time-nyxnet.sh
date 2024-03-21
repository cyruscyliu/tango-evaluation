#!/bin/bash

# We leverage Tango's execution engine to dump the coverage. Specifically, we
# first convert the seeds in the queue of another fuzzer into the seeds of
# Tango-compatible format; next, we reply these seeds one by one to generate a
# sancov file for each seed; subsequently, we extract the edge coverage from the
# sancov files to generate an accumulated edge coverage over time; last, we plot
# the figure for the paper.

# eurosp_data/new_data_for_cov_qiang/workdir_tango_nyxnet/ar/tango_nyxnet/dcmtk/dcmqrscp/0/out-dcmtk-balanced-000/reproducible
# data

eurosp_data='../eurosp_data'

function find_working_dir() {
    target=$1
    if [ "$target" == 'dtls' ]; then
        working_dir=specs/dtls
    elif [ "$target" == 'bftpd' ] || [ "$target" == 'proftpd' ] || [ "$target" == 'lightftp' ] || [ "$target" == 'pureftpd' ]; then
        working_dir=specs/ftp
    elif [ "$target" == 'rtsp' ]; then
        working_dir=specs/rtsp
    elif [ "$target" == 'openssl' ]; then
        working_dir=specs/tls
    elif [ "$target" == 'dcmtk' ]; then
        working_dir=specs/dicom
    elif [ "$target" == 'sip' ]; then
        working_dir=specs/sip
    elif [ "$target" == 'dnsmasq' ]; then
        working_dir=specs/dns
    elif [ "$target" == 'openssh' ]; then
        working_dir=specs/ssh
    else
        echo "Unknown target: $target"
        exit 1
    fi
    echo "$working_dir"
}

# nyxnet
# .
# `-- nyxnet
#     |-- bftpd
#     |   `-- bftpd
#     |       |-- 0
#     |       |   |-- out-bftpd-balanced-000
#     |       |   `-- pcaps_to_replay/queue
nyxnet_dirs=(
    "$eurosp_data"/data_for_cov/ar/nyxnet/
    "$eurosp_data"/data_for_cov/ar/tango_nyxnet/
)

# step 1, convert to pcaps
# - nyxnet
# bftpd  dcmtk  dnsmasq  dtls  lightftp  openssh  openssl  proftpd  pureftpd  rtsp  sip
out_dirs=()
for nyxnet_dir in "${nyxnet_dirs[@]}"; do
    readarray -d '' ds < <(find "$nyxnet_dir" -type d -wholename "*[0,1,2]/out-*-balanced-00[0,1,2]" -print0)
    for d in "${ds[@]}"; do
        out_dirs+=("$d")
    done
done

rm -rf convert-to-pcaps-nyxnet.sh
rm -rf replay-and-dump-coverage-nyxnet.sh
for out_dir in "${out_dirs[@]}"; do
    # get the target: ar/tango_nyxnet/lightftp/lightftp/1/out-lightftp-balanced-000
    IFS='/' read -r -a parts <<< "$out_dir"
    target_index=$((${#parts[@]} - 4))
    target="${parts[target_index]}"

    # currently, pureftpd is not compatible with ASAN
    if [ "$target" == 'pureftpd' ]; then
        continue
    fi

    working_dir=$(find_working_dir "$target")
    out_dir=$(realpath "$out_dir")

    nyx_balanced="$out_dir"/reproducible
    pcaps_to_replay="$out_dir"/../pcaps_to_replay/queue
    echo "pushd $working_dir && rm -rf $pcaps_to_replay && mkdir -p $pcaps_to_replay && \
          python nyx_net_spec.py nyxnet $nyx_balanced $pcaps_to_replay && popd" >> convert-to-pcaps-nyxnet.sh

    echo "pushd /home/tango && python gen_cov.py -C targets/$target/fuzz.json \
         -W $pcaps_to_replay/.. -c /home/tango/targets/$target/ -vv && \
         mkdir -p $pcaps_to_replay/../../workdir && \
         mv $pcaps_to_replay/../pc_cov_cnts.csv $pcaps_to_replay/../../workdir && popd" >> replay-and-dump-coverage-nyxnet.sh
done

pushd /home/tango
source .venv/bin/activate
python="$(realpath "$(which python)")"
sudo setcap \
    cap_net_admin,cap_sys_admin,cap_dac_override,cap_chown,cap_fowner,cap_setpcap,cap_setuid,cap_setgid,cap_sys_ptrace+eip \
    "$python"
popd

sudo apt-get install -y parallel
python -m pip install psutil jinja2 \
    numpy nptyping networkx \
    lru-dict pyroute2 pyelftools posix-ipc aiohttp asynctempfile \
    pydot matplotlib Pillow seaborn asyncstdlib scapy aioconsole \
    scikit-learn cffi msgpack pyshark ipdb --upgrade

# step 1
# parallel -j12 --bar < convert-to-pcaps-nyxnet.sh
# step 2 & 3
# bash -x replay-and-dump-coverage-nyxnet.sh
