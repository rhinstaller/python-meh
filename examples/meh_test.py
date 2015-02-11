#!/usr/bin/python -tbBQnew
# -*- coding: utf-8 -*-

import sys
import meh
import meh.handler
import meh.dump
import subprocess

class MyTestError(Exception):
    pass

class MyObject(object):
    def __init__(self):
        self.unicode_str = u"řčšěčšěčěš"
        self.encoded_unicode_str = self.unicode_str.encode("utf-8")
        self.binary_data = '\xff\xff\xfe'

if __name__ == "__main__":
    print "***Running python-meh test***"

    config = meh.Config(programName="myMehTest", programVersion="1.0-1",
                        programArch="noarch",
                        fileList=["/proc/cmdline", "unicode.txt", "ascii.txt"])

    if len(sys.argv) > 1 and sys.argv[1] == "g":
        import meh.ui.gui
        intf = meh.ui.gui.GraphicalIntf()
    else:
        import meh.ui.text
        intf = meh.ui.text.TextIntf()

    handler = meh.handler.ExceptionHandler(config, intf,
                                            meh.dump.ExceptionDump)
    handler.install(MyObject())

    #raise MyTestError("My testing exception.")
    subprocess.call(["non_existing_executable"])
