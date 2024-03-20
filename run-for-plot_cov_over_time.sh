docker run \
     -v "$PWD"/tango:/home/tango/ \
     -v "$PWD/../eurosp_data/":/home/eurosp_data \
     -v "$PWD":/home/evaluation \
     -w /home/evaluation \
     --entrypoint /bin/bash \
    --rm -it \
    --privileged tango:latest
