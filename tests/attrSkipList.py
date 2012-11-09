import os
import unittest
from tests.baseclass import *

from meh.handler import *
from meh.dump import *

class Example:
    def __init__(self):
        self.rootPassword = "blahblah"
        self.dontSkipMe = 12345

class AttrSkipList_TestCase(BaseTestCase):
    def runTest(self):
        example = Example()

        conf = Config(programName="test",
                      programVersion="47",
                      attrSkipList=[ "rootPassword" ])

        dump = self.dump(conf, example)

        self.assertIn("rootPassword: Skipped", dump)
        self.assertNotIn("dontSkipMe: Skipped", dump)

if __name__ == "__main__":
    unittest.main()
