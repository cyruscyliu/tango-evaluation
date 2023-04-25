from tango.net import PCAPInput

class FMT(object):
    def __init__(self, protocol, port):
        self.endpoint = '127.0.0.1'
        self.protocol = protocol
        self.port = port

def to_pcap(pathname, protocol, port, inp):
    new_inp = PCAPInput(file=pathname, fmt=FMT(protocol, port))
    new_inp.dumpi(inp)
    print('dump to {}'.format(pathname))
