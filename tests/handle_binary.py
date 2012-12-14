# -*- coding: utf-8 -*-

from tests.baseclass import BaseTestCase
from meh import Config

BINARY_DATA = "\xff\xfe\xdd"

class BinaryExample(object):
    def __init__(self):
        self.bin_data = BINARY_DATA

class HandleBinary_TestCase(BaseTestCase):
    def runTest(self):
        binary_example = BinaryExample()

        conf = Config(programName="UnicodeTest",
                      programVersion="1.0")

        # should not raise exception
        dump = self.dump(conf, binary_example)

        self.assertIn("OMITTED BINARY DATA", dump)

