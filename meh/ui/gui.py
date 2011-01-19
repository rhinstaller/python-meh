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
import gtk
import gtk.glade
import os
import report

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

def findGladeFile(file):
    path = os.environ.get("GLADEPATH", "./:ui/:/tmp/updates/:/tmp/updates/ui/:/usr/share/python-meh/")
    for d in path.split(":"):
        fn = d + file
        if os.access(fn, os.R_OK):
            return fn
    raise RuntimeError, "Unable to find glade file %s" % file

def findPixmap(file):
    path = os.environ.get("PIXMAPPATH", "./:pixmaps/:/tmp/updates/:/tmp/updates/pixmaps/:/usr/share/python-meh/")
    for d in path.split(":"):
        fn = d + file
        if os.access(fn, os.R_OK):
            return fn
    return None

class GraphicalIntf(AbstractIntf):
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

    def saveExceptionWindow(self, accountManager, signature, *args, **kwargs):
        win = SaveExceptionWindow(accountManager, signature)
        win.run()

class SaveExceptionWindow(AbstractSaveExceptionWindow):
    def __init__(self, accountManager, signature, *args, **kwargs):
        import report.io.GTKIO

        self.accountManager = accountManager
        self.signature = signature

        self.io = report.io.GTKIO.GTKIO(self.accountManager)

    def run(self, *args, **kwargs):
        # Don't need to check the return value of report since it will
        # handle all the UI reporting for us.
        report.report(self.signature, self.io)

class MainExceptionWindow(AbstractMainExceptionWindow):
    def __init__(self, shortTraceback=None, longTracebackFile=None, *args, **kwargs):
        AbstractMainExceptionWindow.__init__(self, shortTraceback, longTracebackFile,
                                             *args, **kwargs)

        xml = gtk.glade.XML(findGladeFile("detailed-dialog.glade"), domain="python-meh")
        self.dialog = xml.get_widget("detailedDialog")
        self.mainVBox = xml.get_widget("mainVBox")
        self.hbox = xml.get_widget("hbox1")
        self.info = xml.get_widget("info")
        self.detailedExpander = xml.get_widget("detailedExpander")
        self.detailedView = xml.get_widget("detailedView")

        # Set the custom icon.
        img = gtk.Image()
        img.set_from_file(findPixmap("exception.png"))
        self.hbox.pack_start(img)
        self.hbox.reorder_child(img, 0)

        # Set the buttons.
        for (button, response) in [(_("Debu_g"), MAIN_RESPONSE_DEBUG),
                                   ("gtk-save", MAIN_RESPONSE_SAVE),
                                   (_("_Exit"), MAIN_RESPONSE_OK)]:
            self.dialog.add_button(button, response)

        self.dialog.set_default_response(MAIN_RESPONSE_OK)

        self.info.set_text(_("An unhandled exception has occurred.  This "
                             "is most likely a bug.  Please save a copy "
                             "of the detailed exception and file a bug "
                             "report."))

        if longTracebackFile:
            f = open(longTracebackFile)

            textbuf = gtk.TextBuffer()
            i = textbuf.get_start_iter()

            while True:
                # Wish readline would give StopIteration at the end of a file.
                line = f.readline()
                if line == "":
                    break

                if __builtins__.get("type")(line) != unicode:
                    try:
                        line = unicode(line, encoding='utf-8')
                    except UnicodeDecodeError:
                        pass

                textbuf.insert(i, line)

            f.close()
            self.detailedView.set_buffer(textbuf)
        else:
            self.mainVBox.remove(self.detailedExpander)

    def destroy(self, *args, **kwargs):
        self.dialog.destroy()

    def run(self, *args, **kwargs):
        self.dialog.show_all()
        self.rc = self.dialog.run()
        self.dialog.destroy()

class MessageWindow(AbstractMessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        AbstractMessageWindow.__init__(self, title, text, *args, **kwargs)
        self.dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
                                        type=gtk.MESSAGE_INFO,
                                        message_format=text)
        self.dialog.set_title(title)
        self.dialog.set_position(gtk.WIN_POS_CENTER)

    def destroy(self, *args, **kwargs):
        self.dialog.destroy()

    def run(self, *args, **kwargs):
        self.dialog.show_all()
        self.rc = self.dialog.run()
        self.dialog.destroy()

class ExitWindow(MessageWindow):
    def __init__(self, title, text, *args, **kwargs):
        self.dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_NONE,
                                        type=gtk.MESSAGE_INFO,
                                        message_format=text)
        self.dialog.set_title(title)
        self.dialog.add_button(_("_Exit"), 0)
        self.dialog.set_position(gtk.WIN_POS_CENTER)
