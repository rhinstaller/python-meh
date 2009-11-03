import glob
import imputil
import os
import sys
import tempfile
import unittest

from meh.handler import *
from meh.dump import *

class BaseTestCase(unittest.TestCase):
    def dump(self, fd, conf, obj):
        from inspect import stack as _stack
        stack = _stack()[1:]

        dump = ExceptionDump((None, None, stack), conf)
        dump.dump(fd, obj)

    def openFile(self):
        (fd, path) = tempfile.mkstemp()
        fo = os.fdopen(fd, "w")
        return (fo, path)

    def tracebackContains(self, path, str):
        f = open(path)
        while True:
            l = f.readline()
            if l == "":
                f.close()
                return False

            if l.find(str) != -1:
                f.close()
                return True

        f.close()
        return False

def loadModules(moduleDir, cls_pattern="_TestCase", skip_list=["__init__", "baseclass"]):
    '''taken from firstboot/loader.py'''

    # Guaruntee that __init__ is skipped
    if skip_list.count("__init__") == 0:
        skip_list.append("__init__")

    tstList = list()

    # Make sure moduleDir is in the system path so imputil works.
    if not moduleDir in sys.path:
        sys.path.insert(0, moduleDir)

    # Get a list of all *.py files in moduleDir
    moduleList = []
    lst = map(lambda x: os.path.splitext(os.path.basename(x))[0],
              glob.glob(moduleDir + "/*.py"))

    # Inspect each .py file found
    for module in lst:
        if module in skip_list:
            continue

        # Attempt to load the found module.
        try:
            found = imputil.imp.find_module(module)
            loaded = imputil.imp.load_module(module, found[0], found[1], found[2])
        except ImportError, e:
            print("Error loading module %s." % module)
            continue

        # Find class names that match the supplied pattern (default: "_TestCase")
        beforeCount = len(tstList)
        for obj in loaded.__dict__.keys():
            if obj.endswith(cls_pattern):
                tstList.append(loaded.__dict__[obj])
        afterCount = len(tstList)

        # Warn if no tests found
        if beforeCount == afterCount:
            print("Module %s does not contain any test cases; skipping." % module)
            continue

    return tstList

# Run the tests
if __name__ == "__main__":

    # Create a test suite
    MehTestSuite = unittest.TestSuite()

    # Find tests to add
    tstList = loadModules(os.path.join(os.environ.get("PWD"), "tests/"))
    for tst in tstList:
        MehTestSuite.addTest(tst())

    # Run tests
    unittest.main(defaultTest="MehTestSuite")
