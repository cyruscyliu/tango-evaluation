# Let's tango!

## Requirements

+ Linux 5.11
+ nyx-net-profuzzbench
    - git clone git@github.com:cyruscyliu/nyx-net-profuzzbench.git
+ nyx-net
    - git clone git@github.com:cyruscyliu/nyx-net.git
    - source rust.sh
    - ./setup.sh
    - cd targets; decompress_packed_targets.sh
+ tango
    - git clone git@github.com:HexHive/tango.git
+ python 3.11
    - python3.11 -m pip install numpy nptyping networkx \
      lru-dict pyroute2 pyelftools posix-ipc aiohttp asynctempfile \
      pydot matplotlib Pillow seaborn asyncstdlib scapy aioconsole \
      scikit-learn cffi msgpack pyshark ipdb --upgrade

## Convert aflnet/aflpp/nyxnet raw bytes to pcaps

The test case of in AFLNet's `replayable-queue/` has a len-data format. The
first four bytes indicates how long each packet is. However, I guess AFL++ takes
one input as a whole packet. NyxNet uses packet(data) to store packets.

1. Download data into pfb-eval-afl-24h/ and pfb-eval-nyx-24h/.
2. Run `convert-to-pcaps.sh TARGET`
