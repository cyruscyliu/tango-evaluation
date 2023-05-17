#!/bin/bash

for target in `ls pcaps_to_replay`; do
    if [ ${target} == 'forked-daapd' ]; then
        # echo "Not supported yet"
	continue
    elif [ ${target} == 'tinydtls' ]; then
        # echo "Not supported yet"
	continue
    elif [ ${target} == 'bftpd' ]; then
        # echo "Not supported yet"
       	continue
    elif [ ${target} == 'proftpd' ]; then
        # echo "Not supported yet"
	continue
    elif [ ${target} == 'live555' ]; then
        # echo "Not supported yet"
	continue
    elif [ ${target} == 'openssl' ]; then
        working_dir=targets/openssl
    elif [ ${target} == 'dcmtk' ]; then
        working_dir=targets/dcmtk
    elif [ ${target} == 'kamailio' ]; then
        # echo "Not supported yet"
	continue
    elif [ ${target} == 'lightftp' ]; then
        # echo "Not supported yet"
       	continue
    elif [ ${target} == 'pure-ftpd' ]; then
        # echo "Not supported yet"
       	continue
    elif [ ${target} == 'dnsmasq' ]; then
        working_dir=targets/dnsmasq
    elif [ ${target} == 'openssh' ]; then
        working_dir=targets/openssh
    elif [ ${target} == 'exim' ]; then
        working_dir=targets/exim
    else
        echo "Not supported" && continue
    fi

    for out_fuzzer_target_run in `ls pcaps_to_replay/$target`; do
        pushd tango 2>&1 >/dev/null
        pushd $working_dir 2>&1 >/dev/null && \
            rm -f $out_fuzzer_target_run && \
            ln -s ../../../pcaps_to_replay/$target/$out_fuzzer_target_run $out_fuzzer_target_run && \
            popd 2>&1 >/dev/null
        popd 2>&1 >/dev/null
        echo "pushd tango && \
            PYSCRIPT=gen_cov.py ./run.sh $working_dir/fuzz.json $working_dir/$out_fuzzer_target_run && \
            popd"
    done
done
