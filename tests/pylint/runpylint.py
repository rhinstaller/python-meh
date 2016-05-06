#!/usr/bin/python3

import sys

from pocketlint import PocketLintConfig, PocketLinter

class MehLintConfig(PocketLintConfig):
    @property
    def pylintPlugins(self):
        retval = super(MehLintConfig, self).pylintPlugins
        retval.remove("pocketlint.checkers.markup")
        return retval

    @property
    def ignoreNames(self):
        return {"translation-canary"}

if __name__ == "__main__":
    conf = MehLintConfig()
    linter = PocketLinter(conf)
    rc = linter.run()
    sys.exit(rc)
