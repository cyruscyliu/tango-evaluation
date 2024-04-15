#!/bin/bash

cd ../tango
docker run \
     -v "$PWD":/home/tango/ \
     -v "$PWD"/../eurosp_data/:/home/eurosp_data \
     -v "$PWD"/../evaluation:/home/evaluation \
     -w /home/evaluation \
     --entrypoint /bin/bash \
    --rm -it \
    --privileged tango:latest
