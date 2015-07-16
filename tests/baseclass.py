import glob
import importlib
import os
import sys
import tempfile
import unittest
import six

from meh import ExceptionInfo
from meh.dump import ExceptionDump

class BaseTestCase(unittest.TestCase):
    def dump(self, conf, obj):
        from inspect import stack as _stack
        stack = _stack()[1:]

        dump = ExceptionDump(ExceptionInfo(None, None, stack), conf)
        return dump.dump(obj)

    def openFile(self, mode="w"):
        (fd, path) = tempfile.mkstemp()
        # only Python 3 has supports the "encoding" keyword argument
        if six.PY2:
            fo = os.fdopen(fd, mode)
        else:
            fo = os.fdopen(fd, mode, encoding="utf-8")

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

def loadModules(moduleDir, cls_pattern="_TestCase", skip_list=None):
    '''taken from firstboot/loader.py'''

    if not skip_list:
        skip_list = ["__init__", "baseclass"]

    # Guaruntee that __init__ is skipped
    if skip_list.count("__init__") == 0:
        skip_list.append("__init__")

    tstList = list()

    # Make sure moduleDir is in the system path so imputil works.
    if not moduleDir in sys.path:
        sys.path.insert(0, moduleDir)

    # Get a list of all *.py files in moduleDir
    lst = map(lambda x: os.path.splitext(os.path.basename(x))[0],
              glob.glob(moduleDir + "/*.py"))

    # Inspect each .py file found
    for module in lst:
        if module in skip_list:
            continue

        # Attempt to load the found module.
        try:
            loaded = importlib.import_module(module)
        except ImportError:
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
