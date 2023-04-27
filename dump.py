from tango.net import PCAPInput

import struct

class FMT(object):
    def __init__(self, protocol, port):
        self.endpoint = '127.0.0.1'
        self.protocol = protocol
        self.port = port

def to_pcap(pathname, protocol, port, inp):
    new_inp = PCAPInput(file=pathname, fmt=FMT(protocol, port))
    new_inp.dumpi(inp)
    print('dump to {}'.format(pathname))

def split_aflnet_testcase(data, label):
    i = 0
    res = []

    while i < len(data):
        content_len = struct.unpack("<I", data[i: i + 4])[0]
        res.append([label, data[i + 4: i + 4 + content_len]])
        i += (content_len + 4)

    return res
