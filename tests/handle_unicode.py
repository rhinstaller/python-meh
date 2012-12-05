# -*- coding: utf-8 -*-
import tempfile

from tests.baseclass import BaseTestCase
from meh import Config

UNICODE_STR = u"řěšččšě"
UNICODE_LINE = u"řčšřščřčš\n"
ASCII_STR = "fsdkljfdsldfs"
ASCII_LINE = "fdsfsdakjfdsa\n"

class UnicodeExample(object):
    def __init__(self):
        self.ascii_str = ASCII_STR
        self.unicode_str = UNICODE_STR
        self.encoded_str = self.unicode_str.encode("utf-8")
        self.unicode_dict = { u"úú" : u"áá" }

class HandleUnicode_TestCase(BaseTestCase):
    def setUp(self):
        # write UTF-8 and ASCII files for testing
        (fobj, self.uni_file_path) = self.openFile()
        fobj.write(UNICODE_LINE.encode("utf-8"))
        fobj.close()

        (fobj, self.ascii_file_path) = self.openFile()
        fobj.write(ASCII_LINE)
        fobj.close()

    def runTest(self):
        unicode_example = UnicodeExample()

        conf = Config(programName="UnicodeTest",
                      programVersion="1.0",
                      fileList=[self.uni_file_path, self.ascii_file_path])

        # should not raise exception
        dump = self.dump(conf, unicode_example)

        self.assertIn("unicode_str: " + UNICODE_STR.encode("utf-8"), dump)
        self.assertIn("encoded_str: " + UNICODE_STR.encode("utf-8"), dump)
        self.assertIn(UNICODE_LINE.encode("utf-8"), dump)

        self.assertIn("ascii_str: " + ASCII_STR, dump)
        self.assertIn(ASCII_LINE, dump)

