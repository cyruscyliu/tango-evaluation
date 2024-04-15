#!/bin/bash

# make sure we are in the docker container
pushd /home/tango/targets

USE_ASAN=1 DISABLE_TANGOLIB=1 make bftpd/
# USE_ASAN=1 DISABLE_TANGOLIB=1 make daapd/
USE_ASAN=1 DISABLE_TANGOLIB=1 make dcmtk/
USE_ASAN=1 DISABLE_TANGOLIB=1 make dnsmasq/
# USE_ASAN=1 DISABLE_TANGOLIB=1 make exim/
USE_ASAN=1 DISABLE_TANGOLIB=1 make expat/
USE_ASAN=1 DISABLE_TANGOLIB=1 make lightftp/
USE_ASAN=1 DISABLE_TANGOLIB=1 make live555/
USE_ASAN=1 DISABLE_TANGOLIB=1 make llhttp/
USE_ASAN=1 DISABLE_TANGOLIB=1 make openssh/
USE_ASAN=1 DISABLE_TANGOLIB=1 make openssl/
# USE_ASAN=1 DISABLE_TANGOLIB=1 make proftpd/
# USE_ASAN=1 DISABLE_TANGOLIB=1 make pureftpd/
USE_ASAN=1 DISABLE_TANGOLIB=1 make tinydtls/
# USE_ASAN=1 DISABLE_TANGOLIB=1 make kamailio/
USE_ASAN=1 DISABLE_TANGOLIB=1 make yajl/

wait
popd
