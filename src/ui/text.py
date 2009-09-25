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
from snack import *

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

class TextIntf(AbstractIntf):
    def __init__(self, *args, **kwargs):
        AbstractIntf.__init__(self, *args, **kwargs)

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

    def saveExceptionWindow(self, exnFile, desc="", *args, **kwargs):
        win = SaveExceptionWindow(exnFile, desc=desc, *args, **kwargs)
        return win

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

class SaveExceptionWindow(AbstractSaveExceptionWindow):
    def __init__(self, exnFile, desc="", *args, **kwargs):
        AbstractSaveExceptionWindow.__init__(self, exnFile, desc=desc, *args, **kwargs)
        self.screen = kwargs.get("screen", None)
        self._desc = desc
        self._method = "disk"

    def _runSaveToDisk(self):
        toplevel = GridForm(self.screen, _("Save to disk"), 1, 2)

        buttons = ButtonBar(self.screen, [_("OK"), _("Cancel")])
        self.dirEntry = Entry(24)

        entryGrid = Grid(2, 2)
        entryGrid.setField(Label(_("Directory")), 0, 0, anchorLeft=1)
        entryGrid.setField(self.dirEntry, 1, 0)

        toplevel.add(entryGrid, 0, 0, (0, 0, 0, 1))
        toplevel.add(buttons, 0, 1, growx=1)

        result = toplevel.run()
        return buttons.buttonPressed(result)

    def _runSaveToBugzilla(self):
        toplevel = GridForm(self.screen, _("Save to bugzilla"), 1, 2)

        buttons = ButtonBar(self.screen, [_("OK"), _("Cancel")])
        self.bugzillaNameEntry = Entry(24)
        self.bugzillaPasswordEntry = Entry(24, password=1)
        self.bugDesc = Entry(24)

        self.bugDesc.setText(self._desc)

        bugzillaGrid = Grid(2, 3)
        bugzillaGrid.setField(Label(_("Username")), 0, 0, anchorLeft=1)
        bugzillaGrid.setField(self.bugzillaNameEntry, 1, 0)
        bugzillaGrid.setField(Label(_("Password")), 0, 1, anchorLeft=1)
        bugzillaGrid.setField(self.bugzillaPasswordEntry, 1, 1)
        bugzillaGrid.setField(Label(_("Bug Description")), 0, 2, anchorLeft=1)
        bugzillaGrid.setField(self.bugDesc, 1, 2)

        toplevel.add(bugzillaGrid, 0, 0, (0, 0, 0, 1))
        toplevel.add(buttons, 0, 1, growx=1)

        result = toplevel.run()
        return buttons.buttonPressed(result)

    def _runSaveToRemote(self):
        toplevel = GridForm(self.screen, _("Send to remote server (scp)"), 1, 2)

        buttons = ButtonBar(self.screen, [_("OK"), _("Cancel")])
        self.scpNameEntry = Entry(24)
        self.scpPasswordEntry = Entry(24, password=1)
        self.scpHostEntry = Entry(24)
        self.scpDestEntry = Entry(24)

        scpGrid = Grid(2, 4)
        scpGrid.setField(Label(_("User name")), 0, 0, anchorLeft=1)
        scpGrid.setField(self.scpNameEntry, 1, 0)
        scpGrid.setField(Label(_("Password")), 0, 1, anchorLeft=1)
        scpGrid.setField(self.scpPasswordEntry, 1, 1)
        scpGrid.setField(Label(_("Host (host:port)")), 0, 2, anchorLeft=1)
        scpGrid.setField(self.scpHostEntry, 1, 2)
        scpGrid.setField(Label(_("Destination file")), 0, 3, anchorLeft=1)
        scpGrid.setField(self.scpDestEntry, 1, 3)

        toplevel.add(scpGrid, 0, 0, (0, 0, 0, 1))
        toplevel.add(buttons, 0, 1, growx=1)

        result = toplevel.run()
        return buttons.buttonPressed(result)

    def destroy(self, *args, **kwargs):
        self.screen.popWindow()
        self.screen.refresh()

    def run(self, *args, **kwargs):
        mapping = {"disk": self._runSaveToDisk,
                   "bugzilla": self._runSaveToBugzilla,
                   "scp": self._runSaveToRemote}

        toplevel = GridForm(self.screen, _("Save"), 1, 4)

        self.rg = RadioGroup()
        self.diskButton = self.rg.add(_("Save to local"), "disk", True)
        self.bugzillaButton = self.rg.add(_("Save to bugzilla"), "bugzilla", False)
        self.scpButton = self.rg.add(_("Save to remote server (scp)"), "scp", False)

        buttons = ButtonBar(self.screen, [_("OK"), _("Cancel")])

        toplevel.add(self.diskButton, 0, 0, (0, 0, 0, 1))
        toplevel.add(self.bugzillaButton, 0, 1, (0, 0, 0, 1))
        toplevel.add(self.scpButton, 0, 2, (0, 0, 0, 1))
        toplevel.add(buttons, 0, 3, growx=1)

        while True:
            result = toplevel.run()
            rc = buttons.buttonPressed(result)

            if rc == string.lower(_("OK")):
                if mapping[self.rg.getSelection()]() == string.lower(_("Cancel")):
                    self.destroy()
                    continue

                self.rc = SAVE_RESPONSE_OK
                self._method = self.rg.getSelection()
                self.destroy()
            else:
                self.rc = SAVE_RESPONSE_CANCEL

            break

    def getrc(self, *args, **kwargs):
        return self.rc

    def getDest(self, *args, **kwargs):
        if self._method == "disk":
            return (0, self.dirEntry.value())
        elif self._method == "bugzilla":
            return (1, map(lambda e: e.value(), [self.bugzillaNameEntry,
                                                 self.bugzillaPasswordEntry,
                                                 self.bugDesc]))
        elif self._method == "scp":
            return (2, map(lambda e: e.value(), [self.scpNameEntry,
                                                 self.scpPasswordEntry,
                                                 self.scpHostEntry,
                                                 self.scpDestEntry]))
