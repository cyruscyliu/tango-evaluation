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

## Convert aflnet/aflpp/nyxnet raw bytes to pcaps

1. Download data into xxx and xxx.
2. Go into tango's venv.
3. Run `convert-raw-bytes-to-pcap.sh TARGET`
