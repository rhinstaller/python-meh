# Copyright (C) 2009, 2013  Red Hat, Inc.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): Chris Lumens <clumens@redhat.com>
#            Vratislav Podzimek <vpodzime@redhat.com>
#
from meh import *
from meh.ui import *
import report
import report.io.TextIO
from report import LIBREPORT_WAIT, LIBREPORT_RUN_CLI

import os

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

class TextWindow(object):
    """Helper class providing some common methods needed by all text windows."""

    def __init__(self, title, *args, **kwargs):
        self._title = title

        # XXX: I know this must be really hard for translators, but there is no
        #      usable way to include context to the POT file in Python
        self._yes_answer = _("y")
        self._no_answer = _("n")

    @property
    def _usable_width(self):
        return os.environ.get("COLUMNS", 80) - 1

    def _print_rule(self):
        rule = self._usable_width * "="
        print rule

    def print_header(self):
        print
        self._print_rule()
        print self._title
        self._print_rule()

    def destroy(self):
        self._print_rule()
        self._print_rule()

class TextIntf(AbstractIntf):
    def __init__(self, *args, **kwargs):
        AbstractIntf.__init__(self, *args, **kwargs)
        self.screen = kwargs.get("screen", None)

    def enableNetwork(self, *args, **kwargs):
        """Should be provided by the inheriting class."""

        return False

    def exitWindow(self, title, message, *args, **kwargs):
        win = ExitWindow(title, message, *args, **kwargs)
        win.run()
        win.destroy()

    def mainExceptionWindow(self, text, exnFile, *args, **kwargs):
        win = MainExceptionWindow(text, exnFile, *args, **kwargs)
        return win

    def messageWindow(self, title, message, *args, **kwargs):
        win = MessageWindow(title, message, *args, **kwargs)
        win.run()
        win.destroy()

    def saveExceptionWindow(self, signature, *args, **kwargs):
        win = SaveExceptionWindow(signature, *args, **kwargs)
        win.run()
        win.destroy()

class SaveExceptionWindow(TextWindow, AbstractSaveExceptionWindow):
    def __init__(self, signature, *args, **kwargs):
        AbstractSaveExceptionWindow.__init__(self, signature,
                                             *args, **kwargs)
        TextWindow.__init__(self, _("Save exception"), *args, **kwargs)
        self.signature = signature

    def run(self, *args, **kwargs):
        # Don't need to check the return value of report since it will
        # handle all the UI reporting for us.
        report.report_problem_in_memory(self.signature,
                                        LIBREPORT_WAIT|LIBREPORT_RUN_CLI)

class MainExceptionWindow(TextWindow, AbstractMainExceptionWindow):
    def __init__(self, shortTraceback=None, longTraceback=None, *args, **kwargs):
        AbstractMainExceptionWindow.__init__(self, shortTraceback, longTraceback,
                                             *args, **kwargs)
        TextWindow.__init__(self, _("An unknown error has occurred"),
                            *args, **kwargs)
        self._short_traceback = shortTraceback
        self._menu_items = [(_("Report Bug"), MAIN_RESPONSE_SAVE),
                            (_("Debug"), MAIN_RESPONSE_DEBUG),
                            (_("Quit"), MAIN_RESPONSE_QUIT)]

    def run(self, *args, **kwargs):
        self.print_header()
        print self._short_traceback
        print _("What do you want to do now?")
        for (idx, item) in enumerate(self._menu_items):
            print "%d) %s" % (idx + 1, item[0])

        ret = -1
        num_menu_items = len(self._menu_items)
        print
        while not (0 < ret <= num_menu_items):
            ret = raw_input(_("Please make your choice from above: "))
            try:
                ret = int(ret)
            except ValueError:
                ret = -1

        return self._menu_items[ret - 1][1]

class MessageWindow(TextWindow, AbstractMessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        AbstractMessageWindow.__init__(self, title, text, *args, **kwargs)
        TextWindow.__init__(self, title, *args, **kwargs)
        self._text = text

    def run(self, *args, **kwargs):
        self.print_header()
        print self._text
        print
        raw_input(_("Hit ENTER to continue"))

class ExitWindow(MessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        MessageWindow.__init__(self, title, text, *args, **kwargs)

    def run(self, *args, **kwargs):
        self.print_header()
        print self._text
        print

        # self._no_answer may be non-ascii string (simple .upper() doesn't work)
        no_answer_upper = self._no_answer.decode("utf-8").upper().encode("utf-8")
        answer = raw_input(_("Are you sure you want to exit? [%(yes)s/%(no)s]") %
                           { "yes": self._yes_answer,
                             "no": no_answer_upper })

        # no answer means accepting the default (self._no_answer) and the answer
        # is case insensitive (and may be non-ascii)
        lower_answer = answer.decode("utf-8").lower().encode("utf-8")
        answer = lower_answer or self._no_answer

        if answer in (self._yes_answer, self._no_answer):
            return answer == self._yes_answer
        else:
            self.run(*args, **kwargs)
