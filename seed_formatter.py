#!/usr/bin/python3
""" Convert different seed formats to PCAPs.

* Tango uses pcaps by default.
* AFLNet and StateAFL uses 4 bytes as the length of the following data.
* AFL++ and SGFuzz takes one input as a whole packet.
* NyxNet defines its own format.

Note: some code is copied from Tango. But this code is simplified to be
generic. Should be OK if Tango updates.
"""

import os
import time
import struct
import random
import argparse

from scapy.all import Ether, IP, TCP, UDP, PcapWriter, Raw, resolve_iface, conf
from typing import ByteString, Iterable

class AbstractInstruction(object):
    pass

class TransmitInstruction(AbstractInstruction):
    def __init__(self, data: ByteString):
        self._data = data

class ReceiveInstruction(AbstractInstruction):
    def __init__(self, size: int=0, data: ByteString=None, expected: ByteString=None):
        self._size = size
        self._expected = expected
        self._data = data

class DelayInstruction(AbstractInstruction):
    def __init__(self, time: float):
        self._time = float(time)

class FMT(object):
    def __init__(self, protocol, port):
        self.endpoint = '127.0.0.1'
        self.protocol = protocol
        self.port = port

class GenericInput(object):
    DELAY_THRESHOLD = 1

    def __init__(self, input, output, target):
        self.input = input
        self.output = output
        self.target = target

        if target == 'bftpd': self.fmt = FMT('tcp', 2100)
        elif target == 'daapd': self.fmt = FMT('tcp', 3689)
        elif target == 'dcmtk': self.fmt = FMT('tcp', 5158)
        elif target == 'dnsmasq': self.fmt = FMT('udp', 5355)
        elif target == 'exim': self.fmt = FMT('tcp', 2025)
        elif target == 'kamailio': self.fmt = FMT('udp', 5060)
        elif target == 'lightftp': self.fmt = FMT('tcp', 2100)
        elif target == 'live555': self.fmt = FMT('tcp', 8554)
        elif target == 'openssh': self.fmt = FMT('tcp', 2022)
        elif target == 'openssl': self.fmt = FMT('tcp', 4433)
        elif target == 'proftpd': self.fmt = FMT('tcp', 2100)
        elif target == 'pureftpd': self.fmt = FMT('tcp', 2100)
        elif target == 'tinydtls': self.fmt = FMT('udp', 20220)

    def dumpi(self, itr: Iterable[AbstractInstruction], output=None):
        def tcp_flow_gen(**kwargs):
            src, dst, data = yield TCP
            seq = {peer: 1 for peer in (src, dst)}
            while True:
                nsrc, ndst, ndata = yield TCP(**kwargs, sport=src, dport=dst,
                    flags='PA', seq=seq[src], ack=seq[dst]) / Raw(load=data)
                seq[src] += len(data)
                src, dst, data = nsrc, ndst, ndata

        def udp_datagram_gen(**kwargs):
            src, dst, data = yield UDP
            while True:
                src, dst, data = yield UDP(**kwargs,
                    sport=src, dport=dst) / Raw(load=data)

        cli = random.randint(40000, 65534)
        srv = self.fmt.port
        iface = resolve_iface(conf.route.route(self.fmt.endpoint)[0])

        layermap = {'tcp': tcp_flow_gen, 'udp': udp_datagram_gen}
        gen_fn = layermap.get(self.fmt.protocol)
        if not gen_fn:
            raise NotImplementedError
        gen = gen_fn()
        gen.send(None)
        cur_time = time.time()
        client_sent = False

        writer = None
        if output is not None:
            print(f"Writing to {output}")
            writer = PcapWriter(output)

        for instruction in itr:
            if isinstance(instruction, DelayInstruction):
                if instruction._time >= self.DELAY_THRESHOLD:
                    cur_time += instruction._time
                continue
            elif isinstance(instruction, TransmitInstruction):
                src, dst = cli, srv
                client_sent = True
            elif isinstance(instruction, ReceiveInstruction):
                if not client_sent:
                    continue
                src, dst = srv, cli

            p = Ether(src=iface.mac, dst=iface.mac) / IP() / \
                    gen.send((src, dst, instruction._data))
            p.time = cur_time

            if writer:
                writer.write(p)

    def get_a_seed(self):
        if os.path.isdir(self.input):
            for filename in os.listdir(self.input):
                yield os.path.join(self.input, filename), \
                    os.path.join(self.output, filename)
        else:
            yield self.input, self.output

    def get_a_packet(self, filename):
        with open(filename, mode='rb') as f:
            for packet in self.split_seed():
                yield packet

    def split_seed(self, data: ByteString):
        for i in range(0, len(data), 1500):
            yield [self.fuzzer, data[i: i + 1500]]

    def convert_to_pcaps(self):
        for seed, output in self.get_a_seed():
            assert(os.path.isfile(seed))
            mtime = os.stat(seed).st_mtime_ns / 1000000000
            tx_ins = []
            for _, packet in self.get_a_packet(seed):
                tx_ins.append(TransmitInstruction(packet+b'\r\n\r\n'))
            try:
                self.dumpi(tx_ins, output=output)
            except struct.error as e:
                print(e)
            os.utime(output, (mtime, mtime))

class AFLNetInput(GenericInput):
    def __init__(self, input: str, output: str, target: str) -> None:
        super().__init__(input, output, target)
        self.fuzzer = 'aflnet'

    def split_seed(self, data: ByteString):
        i = 0
        res = []
        label = self.fuzzer
        while i < len(data):
            content_len = struct.unpack("<I", data[i: i + 4])[0]
            res.append([label, data[i + 4: i + 4 + content_len]])
            i += (content_len + 4)
        return res

class StateAFL(AFLNetInput):
    def __init__(self, input: str, output: str, target: str) -> None:
        super().__init__(input, output, target)
        self.fuzzer = 'stateafl'

class AFLPlusPlus(GenericInput):
    def __init__(self, input: str, output: str, target: str) -> None:
        super().__init__(input, output, target)
        self.fuzzer = 'aflpp'

class NyxNet(GenericInput):
    def __init__(self, input: str, output: str, target: str) -> None:
        super().__init__(input, output, target)
        self.fuzzer = 'nyxnet'

    def get_a_packet(self, filename):
        def packet(data):
            return bytes(data, 'latin-1')

        with open(filename, mode='r') as f:
            for line in f:
                yield [self.fuzzer, eval(line.strip())]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert different seed format PCAPs.")
    parser.add_argument("--fuzzer", help="Name of the fuzzer", type=str, required=True)
    parser.add_argument("--target", help="Name of the target", type=str, required=True)
    parser.add_argument("--output", help="Specify the output path to a seed or queue", type=str)
    parser.add_argument("input", help="Specify the input path to a seed or queue", type=str)

    args = parser.parse_args()
    fuzzer = args.fuzzer
    generic_args = (args.input, args.output, args.target)
    if fuzzer == "aflnet":
        generic_input = AFLNetInput(*generic_args)
    elif fuzzer == "stateafl":
        generic_input = StateAFL(*generic_args)
    elif fuzzer == "aflpp":
        generic_input = AFLPlusPlus(*generic_args)
    elif fuzzer == "nyxnet":
        generic_input = NyxNet(*generic_args)
    else:
        raise NotImplementedError

    generic_input.convert_to_pcaps()
