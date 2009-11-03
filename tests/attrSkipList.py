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

        (fd, path) = self.openFile()
        self.dump(fd, conf, example)
        fd.close()

        self.assertTrue(self.tracebackContains(path, "rootPassword: Skipped"))
        self.assertFalse(self.tracebackContains(path, "dontSkipMe: Skipped"))

if __name__ == "__main__":
    unittest.main()
