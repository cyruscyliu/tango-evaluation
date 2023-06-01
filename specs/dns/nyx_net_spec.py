import sys, os
sys.path.insert(1, os.path.realpath('../..'))
sys.path.insert(1, os.path.realpath('../../tango'))
from tango.core import TransmitInstruction
from dump import to_pcap, split_aflnet_testcase

from spec_lib.graph_spec import *
from spec_lib.data_spec import *
from spec_lib.graph_builder import *
from spec_lib.generators import opts,flags,limits,regex

PROTOCOL='udp'
PORT=5354
import jinja2

s = Spec()
s.use_std_lib = False
s.includes.append("\"custom_includes.h\"")
s.includes.append("\"nyx.h\"")
s.interpreter_user_data_type = "socket_state_t*"

with open("send_code.include.c") as f:
    send_code = f.read()

d_byte = s.data_u8("u8", generators=[limits(0x0, 0xff)])

d_bytes = s.data_vec("pkt_content", d_byte, size_range=(0,1<<12), generators=[]) #regex(pkt)

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

import pyshark
import glob
import ipdb

def split_packets(data, fuzzer):
    if fuzzer == 'aflnet':
        return split_aflnet_testcase(data, 'dns')
    elif fuzzer == 'aflpp':
        res = []
        for i in range(0, len(data), 1500):
            res.append(['dns', data[i: i+1500]])
        return res
    else:
        i = 0
        res = []
        while i*6 < len(data):
            tt,content_len = struct.unpack(">2sI",data[i:i+6])
            res.append( ["dicom", data[i:i+content_len]] )
            i+=(content_len+6)
        return res

instructions = []

def stream_to_bin(path, stream, fuzzer):
    nodes = split_packets(stream, fuzzer)

    for (ntype, content) in nodes:
        ins = TransmitInstruction(content)
        instructions.append(ins)

def packet(data):
    return bytes(data, 'latin-1')

def main():
    if len(sys.argv) != 4:
        print('missing the fuzzer, the source of raw bytes and the destination directory')
        exit(1)

    fuzzer = sys.argv[1]
    src = sys.argv[2]
    dst = sys.argv[3]

    for testcase in os.listdir(src):
        if not os.path.isfile(os.path.join(src, testcase)):
            continue
        b = Builder(s)
        print('handle {}'.format(os.path.join(src,testcase)))
        if fuzzer == 'nyxnet':
            instructions.clear()
            with open(os.path.join(src, testcase), mode='r') as f:
                for line in f:
                    ins = TransmitInstruction(eval(line.strip()))
                    instructions.append(ins)
                mtime = os.stat(os.path.join(src, testcase)).st_mtime_ns / 1000000000
                to_pcap(os.path.join(dst, testcase), PROTOCOL, PORT, instructions, mtime)
        else:
            with open(os.path.join(src, testcase), mode='rb') as f:
                instructions.clear()
                stream_to_bin(os.path.join(src, testcase), f.read(), fuzzer)
                mtime = os.stat(os.path.join(src, testcase)).st_mtime_ns / 1000000000
                to_pcap(os.path.join(dst, testcase), PROTOCOL, PORT, instructions, mtime)

if __name__ == '__main__':
    main()
