# Copyright (C) 2009  Red Hat, Inc.
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
#
from meh import *
from meh.ui import *
import report
from snack import *

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

class TextIntf(AbstractIntf):
    def __init__(self, *args, **kwargs):
        AbstractIntf.__init__(self, *args, **kwargs)
        self.screen = kwargs.get("screen", None)

    def exitWindow(self, title, message, *args, **kwargs):
        win = ExitWindow(title, message, *args, screen = self.screen)
        win.run()
        win.destroy()

    def mainExceptionWindow(self, text, exnFile, *args, **kwargs):
        win = MainExceptionWindow(text, exnFile, *args, screen = self.screen)
        return win

    def messageWindow(self, title, message, *args, **kwargs):
        win = MessageWindow(title, message, *args, screen = self.screen)
        win.run()
        win.destroy()

    def saveExceptionWindow(self, accountManager, signature, *args, **kwargs):
        win = SaveExceptionWindow(accountManager, signature, screen = self.screen)
        win.run()

class SaveExceptionWindow(AbstractSaveExceptionWindow):
    def __init__(self, accountManager, signature, *args, **kwargs):
        import report.io.NewtIO

        self.accountManager = accountManager
        self.signature = signature
        self.screen = kwargs.get("screen")

        self.io = report.io.NewtIO.NewtIO(self.screen)

    def run(self, *args, **kwargs):
        # Don't need to check the return value of report since it will
        # handle all the UI reporting for us.
        report.report(self.signature, self.io)

class MainExceptionWindow(AbstractMainExceptionWindow):
    def __init__(self, shortTraceback=None, longTracebackFile=None, *args, **kwargs):
        AbstractMainExceptionWindow.__init__(self, shortTraceback, longTracebackFile,
                                             *args, **kwargs)

        self.text = "%s\n\n" % shortTraceback
        self.screen = kwargs.get("screen", None)

        self.buttons=[_("OK"), _("Save"), _("Debug")]

    def destroy(self, *args, **kwargs):
        self.screen.popWindow()
        self.screen.refresh()

    def getrc(self, *args, **kwargs):
        if self.rc == string.lower(_("Debug")):
            return MAIN_RESPONSE_DEBUG
        elif self.rc == string.lower(_("Save")):
            return MAIN_RESPONSE_SAVE
        else:
            return MAIN_RESPONSE_OK

    def run(self, *args, **kwargs):
        self.rc = ButtonChoiceWindow(self.screen, _("Exception Occurred"),
                                     self.text, self.buttons)

class MessageWindow(AbstractMessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        AbstractMessageWindow.__init__(self, title, text, *args, **kwargs)
        self.screen = kwargs.get("screen", None)
        self.title = title
        self.text = text

    def run(self, *args, **kwargs):
        self.rc = ButtonChoiceWindow(self.screen, self.title, self.text,
                                     width=60, buttons=[_("OK")])

    def destroy(self, *args, **kwargs):
        self.screen.popWindow()
        self.screen.refresh()

class ExitWindow(MessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        self.screen = kwargs.get("screen", None)
        self.title = title
        self.text = text

    def run(self, *args, **kwargs):
        self.rc = ButtonChoiceWindow(self.screen, self.title, self.text,
                                     width=60, buttons=[_("Exit")])

    def destroy(self, *args, **kwargs):
        self.screen.popWindow()
        self.screen.refresh()
