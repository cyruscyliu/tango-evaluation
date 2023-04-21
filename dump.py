from tango.net import PCAPInput
from tango.core import TransmitInstruction

class FMT(object):
    def __init__(self, protocol, port):
        self.protocol = protocol
        self.port = port

def to_pcap(pathname, protocol, port, inp, name='none'):
    new_inp = PCAPInput(file=pathname, fmt=FMT(protocol, port))
    new_inp.dump(inp, name=name)
    print('dump to {}'.format(pathname))
