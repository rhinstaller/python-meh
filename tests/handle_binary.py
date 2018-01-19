from tests.baseclass import BaseTestCase
from meh import Config

BINARY_DATA = b"\xff\x61\xfe\xdd"
BINARY_DATA2 = b"\xfe\x61\xff\xdd"
BINARY_DATA3 = b"\xfe\x62\xff\xdd"

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
        self.assertTrue("bin_data: \\xff\\x61\\xfe\\xdd\n" in dump or
                        "bin_data: b'\\xffa\\xfe\\xdd'\n" in dump)

        # should contain the binary-keyed dict
        self.assertTrue("dict: {'\\xfe\\x61\\xff\\xdd': \\xfe\\x61\\xff\\xdd" in dump or
                        "dict: {b'\\xfea\\xff\\xdd': b'\\xfea\\xff\\xdd'" in dump)

        # should contain the list with binary item(s)
        self.assertTrue("list: [\\xfe\\x62\\xff\\xdd]" in dump or
                        "list: [b'\\xfeb\\xff\\xdd']" in dump)
