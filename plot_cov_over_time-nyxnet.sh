#!/bin/bash -x
# RUN IN A DOCKER CONTAINER

# We leverage Tango's execution engine to dump the coverage. Specifically, we
# first convert the seeds in the queue of another fuzzer into the seeds of
# Tango-compatible format; next, we reply these seeds one by one to generate a
# sancov file for each seed; subsequently, we extract the edge coverage from the
# sancov files to generate an accumulated edge coverage over time; last, we plot
# the figure for the paper.

eurosp_data=$(realpath '../eurosp_data')
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
out_dirs=()
for nyxnet_dir in "${nyxnet_dirs[@]}"; do
    readarray -d '' ds < <(find "$nyxnet_dir" -type d -name "out-*-balanced-00[0,1,2]" -print0)
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
    # currently, in magma, tango_nyxnet cannot fuzz kamailio and proftpd
    if [ "$target" == 'kamailio' ]; then
        continue
    fi
    if [ "$target" == 'proftpd' ]; then
        continue
    fi

    out_dir=$(realpath "$out_dir")

    nyx_balanced="$out_dir"/reproducible
    pcaps_to_replay="$out_dir"/../pcaps_to_replay/queue
    echo "rm -rf $pcaps_to_replay && mkdir -p $pcaps_to_replay && \
          python seed_formatter.py --fuzzer nyxnet --target $target --output $pcaps_to_replay $nyx_balanced" \
          >> convert-to-pcaps-nyxnet.sh

    echo "pushd /home/tango && python gen_cov.py -C targets/$target/fuzz.json \
         -W $pcaps_to_replay/.. -c /home/tango/targets/$target/ -vv && \
         mkdir -p $pcaps_to_replay/../../workdir && \
         mv $pcaps_to_replay/../pc_cov_cnts.csv $pcaps_to_replay/../../workdir && popd" >> replay-and-dump-coverage-nyxnet.sh
done

# step 1
# parallel -j12 --bar < convert-to-pcaps-nyxnet.sh
# step 2 & 3
# bash -x replay-and-dump-coverage-nyxnet.sh
