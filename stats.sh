#!/bin/bash

for target in pcaps_to_replay/*; do
    for run in $target/*; do
        printf '...%5d... %s\n' `ls $run | wc -l` $run
    done
done
