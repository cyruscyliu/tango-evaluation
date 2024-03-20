from tango.net import PCAPInput

import os
import struct

class FMT(object):
    def __init__(self, protocol, port):
        self.endpoint = '127.0.0.1'
        self.protocol = protocol
        self.port = port

def to_pcap(pathname, protocol, port, inp, mtime):
    new_inp = PCAPInput(file=pathname, fmt=FMT(protocol, port))
    try:
        new_inp.dumpi(inp)
    except struct.error as e:
        print(e)
    new_inp._file.close()
    print('dump to {}'.format(pathname))
    os.utime(pathname, (mtime, mtime))


def split_aflnet_testcase(data, label):
    i = 0
    res = []

    while i < len(data):
        content_len = struct.unpack("<I", data[i: i + 4])[0]
        res.append([label, data[i + 4: i + 4 + content_len]])
        i += (content_len + 4)

    return res
