#!/bin/bash

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
