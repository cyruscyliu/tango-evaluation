import os
import sys

sys.path.insert(1, os.path.join(os.getcwd(), 'tango'))
print(sys.path)

from tango.raw import RawInput
from tango.core import FormatDescriptor

from spec_lib.graph_spec import *
from spec_lib.data_spec import *
from spec_lib.graph_builder import *
from spec_lib.generators import opts,flags,limits,regex

def main():
    targets = [
        'tango_seeds/expat',
        'tango_seeds/yajl',
        'tango_seeds/llhttp',
    ]

    fmt = FormatDescriptor('raw')

    for target in targets:
        for seed in os.listdir(target):
            inp = RawInput(file=os.path.join(target, seed), fmt=fmt)
            for inst in inp.loadi():
                print(inst._data)
            break

    print('hello world')

if __name__ == '__main__':
    main()
