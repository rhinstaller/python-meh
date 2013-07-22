# -*- coding: utf-8 -*-

from tests.baseclass import BaseTestCase
from meh import Config

BINARY_DATA = "\xff\x61\xfe\xdd"
BINARY_DATA2 = "\xfe\x61\xff\xdd"
BINARY_DATA3 = "\xfe\x62\xff\xdd"

class BinaryExample(object):
    def __init__(self):
        self.bin_data = BINARY_DATA

        # crazy, but possible
        self.dict = dict()
        self.dict[BINARY_DATA2] = BINARY_DATA2

        self.list = [BINARY_DATA3]

class HandleBinary_TestCase(BaseTestCase):
    def runTest(self):
        binary_example = BinaryExample()

        conf = Config(programName="UnicodeTest",
                      programVersion="1.0")

        # should not raise exception
        dump = self.dump(conf, binary_example)

        # should contain the attribute name and hexa representation of binary
        # data ('\x61' == 'a' which shouldn't be translated)
        self.assertIn("bin_data: \\xff\\x61\\xfe\\xdd\n", dump)

        # should contain the binary-keyed dict
        self.assertIn("dict: {'\\xfe\\x61\\xff\\xdd': \\xfe\\x61\\xff\\xdd", dump)

        # should contain the list with binary item(s)
        self.assertIn("list: [\\xfe\\x62\\xff\\xdd]", dump)
