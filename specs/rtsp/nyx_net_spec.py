import sys, os
sys.path.insert(1, os.path.realpath('../..'))
sys.path.insert(1, os.path.realpath('../../tango'))
from tango.core import TransmitInstruction
from dump import to_pcap

from spec_lib.graph_spec import *
from spec_lib.data_spec import *
from spec_lib.graph_builder import *
from spec_lib.generators import opts,flags,limits,regex

PROTOCOL='tcp'
PORT=8554
import jinja2

s = Spec()
s.use_std_lib = False
s.includes.append("\"custom_includes.h\"")
s.includes.append("\"nyx.h\"")
s.interpreter_user_data_type = "socket_state_t*"

with open("send_code.include.c") as f:
    send_code = f.read()

with open("send_code_raw.include.c") as f:
    send_code_raw = f.read()

d_byte = s.data_u8("u8", generators=[limits(0x20, 0x7f)])

method="(OPTIONS|DESCRIBE|SETUP|TEARDOWN|PLAY|PAUSE|GET_PARAMETER|SET_PARAMETER|REDIRECT|RECORD|ANNOUNCE|REGISTER|DREGISTER|GET|POST)"
url="rtsp://127\\.0\\.0\\.1:8554/(wavAudioTest|ac3AudioTest|matroskaFileTest|webmFileTest)(/track1)?"
prot="RTSP/1\\.0"
req = method+" "+url+" "+prot+"\\r\\n"

cseq="CSeq: (1|2|3|4|5|6|7|8|9|[0-9]+)"
useragent="User-Agent: \\./testRTSPClient \\(LIVE555 Streaming Media v2018\\.08\\.28\\)"
accept="Accept: application/sdp"
transport="Transport: (RTP/AVP/TCP|RAW/RAW/UDP|MP2T/H2221/UDP);unicast;client_port=37952-37953" # add: destination= interleaved=
rng="Range: npt=(0\\.000-|9)"
session="Session: 000022B8"
field="(%s|%s|%s|%s|%s|%s)"%(cseq,useragent,accept,transport,rng,session)
fields = "((%s\\r\\n)*%s)?"%(field,field)
pkt = req+fields

d_bytes = s.data_vec("pkt_content", d_byte, size_range=(0,1<<12)) #, generators=[regex(pkt)])

n_pkt = s.node_type("packet", interact=True, data=d_bytes, code=send_code)
n_pkt = s.node_type("packet_raw", interact=True, data=d_bytes, code=send_code_raw)

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

def split_packets(data):
        return [["rtsp_packet", d] for d in data.split(b"\r\n\r\n") if len(d) > 0]

instructions = []

def stream_to_bin(path,stream):
    nodes = split_packets(stream)

    for (ntype, content) in nodes:
        ins = TransmitInstruction(content+b'\r\n\r\n')
        instructions.append(ins)

def main():
    if len(sys.argv) != 3:
        print('missing the source of raw bytes and the destination directory')
        exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    for testcase in os.listdir(src):
        if not os.path.isfile(os.path.join(src, testcase)):
            continue
        b = Builder(s)
        print('handle {}'.format(os.path.join(src,testcase)))
        with open(os.path.join(src, testcase), mode='rb') as f:
            instructions.clear()
            stream_to_bin(os.path.join(src, testcase), f.read())
            to_pcap(os.path.join(dst, testcase), PROTOCOL, PORT, instructions)

if __name__ == '__main__':
    main()
