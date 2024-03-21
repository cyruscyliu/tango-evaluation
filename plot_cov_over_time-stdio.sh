#!/bin/bash

# We leverage Tango's execution engine to dump the coverage. Specifically, we
# first reply these seeds one by one to generate a sancov file for each seed;
# next, we extract the edge coverage from the sancov files to generate an
# accumulated edge coverage over time; last, we plot the figure for the paper.

# eurosp_data/old_data_for_cov_ahmad/afl_without_inference/ar/afl_nyx/expat/xmlwf/0/default/queue
# data

eurosp_data=$(realpath '../eurosp_data')
# afl_nyx
# .
# `-- afl_nyx
#     |-- expat
#     |   `-- xmlwf
#     |       |-- 0
#     |       |   |-- default
#     |       |   |   `-- queue
#     |       |   `-- workdir
aflnyx_dirs=(
    "$eurosp_data"/old_data_for_cov_ahmad/afl_with_inference/ar/
    "$eurosp_data"/old_data_for_cov_ahmad/afl_without_inference/ar
)

# step 1, convert to pcaps
# - afl_nyx
# llhttp expat yajl
out_dirs=()
for aflnyx_dir in "${aflnyx_dirs[@]}"; do
    readarray -d '' ds < <(find "$aflnyx_dir" -type d -wholename "*/[0,1,2]/default/queue" -print0)
    for d in "${ds[@]}"; do
        out_dirs+=("$d")
    done
done

rm -rf replay-and-dump-coverage-stdio.sh
for out_dir in "${out_dirs[@]}"; do
    # get the target: ar/afl_nyx/expat/xmlwf/0/default/queue
    IFS='/' read -r -a parts <<< "$out_dir"
    target_index=$((${#parts[@]} - 5))
    target="${parts[target_index]}"

    echo "pushd /home/tango && python gen_cov.py -C targets/$target/fuzz.json \
         -W $out_dir/.. -c /home/tango/targets/$target/ -vv && \
         mv $out_dir/../pc_cov_cnts.csv $out_dir/../../workdir && popd" >> replay-and-dump-coverage-stdio.sh
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

# step 1 & 2
bash -x replay-and-dump-coverage-stdio.sh
