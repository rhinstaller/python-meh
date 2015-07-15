#!/usr/bin/python3

import os

from pocketlint import PocketLintConfig, PocketLinter

class MehLintConfig(PocketLintConfig):
    @property
    def pylintPlugins(self):
        retval = super(MehLintConfig, self).pylintPlugins
        retval.remove("pocketlint.checkers.eintr")
        retval.remove("pocketlint.checkers.markup")
        return retval

if __name__ == "__main__":
    conf = MehLintConfig()
    linter = PocketLinter(conf)
    rc = linter.run()
    os._exit(rc)

