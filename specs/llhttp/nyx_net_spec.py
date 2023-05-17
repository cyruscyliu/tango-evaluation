import sys, os
sys.path.insert(1, os.path.realpath('../..'))
sys.path.insert(1, os.path.realpath('../../tango'))
from tango.raw import RawInput
from tango.core import FormatDescriptor

from spec_lib.graph_spec import *
from spec_lib.data_spec import *
from spec_lib.graph_builder import *
from spec_lib.generators import opts,flags,limits,regex

import jinja2

def get_http_regex():
    return None

s = Spec()
s.use_std_lib = False
s.includes.append("\"custom_includes.h\"")
s.includes.append("\"nyx.h\"")
s.interpreter_user_data_type = "fd_state_t*"

with open("send_code.include.c") as f:
    send_code = f.read()

d_byte = s.data_u8("u8", generators=[limits(0x0, 0xff)])

d_bytes = s.data_vec("pkt_content", d_byte, size_range=(0,1<<12), generators=[]) # regex(get_http_regex())

n_pkt = s.node_type("packet", interact=True, data=d_bytes, code=send_code)

snapshot_code="""
//hprintf("ASKING TO CREATE SNAPSHOT\\n");
kAFL_hypercall(HYPERCALL_KAFL_CREATE_TMP_SNAPSHOT, 0);
kAFL_hypercall(HYPERCALL_KAFL_USER_FAST_ACQUIRE, 0);
//hprintf("RETURNING FROM SNAPSHOT\\n");
vm->ops_i -= OP_CREATE_TMP_SNAPSHOT_SIZE;
"""
n_close = s.node_type("create_tmp_snapshot", code=snapshot_code)

s.build_interpreter()

import msgpack
serialized_spec = s.build_msgpack()
with open("nyx_net_spec.msgp","wb") as f:
    f.write(msgpack.packb(serialized_spec))


def split_packets(path):
    res = []
    inp = RawInput(file=path, fmt=FormatDescriptor('raw'))
    for inst in inp.loadi():
        res.append(['llhttp', inst._data])
    return res

def stream_to_bin(path):
    nodes = split_packets(path)

    for (ntype, content) in nodes:
        b.packet(content)
    path = path.replace('raw_seeds', 'seeds')
    b.write_to_file(path+".bin")

import glob
import ipdb

# convert tango samples
for path in glob.glob("raw_seeds/*"):
    b = Builder(s)
    stream_to_bin(path)
