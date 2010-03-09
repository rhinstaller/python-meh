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
import bdb
import os
from network import hasActiveNetDev
import signal
import sys

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

class NoNetwork(Exception):
    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return "No network is available"

class ExceptionHandler(object):
    def __init__(self, confObj, intfClass, exnClass):
        """Create a new ExceptionHandler instance.  Subclasses of this one may
           be created, provided they are careful to provide all the methods
           this one does.  Instance attributes:

           conf     -- A filled in Config instance.  At least the programName
                       and programVersion are required.
           exnClass -- An instance of ExceptionDump or a subclass of it.  This
                       is required to know how to represent the Python
                       exception internally.
           intf     -- An instance of AbstractIntf.  This is required to know
                       what UI classes to use.
        """
        self.conf = confObj
        self.exnClass = exnClass
        self.intf = intfClass

        self._exitcode = 10
        self._exn = None

        self.conf._intf = self.intf

    def _setExitCode(self, code):
        self._exitcode = code

    exitcode = property(lambda s: s._exitcode,
                        lambda s, v: s._setExitCode(v))

    def _setExn(self, e):
        self._exn = e

    exn = property(lambda s: s._exn,
                   lambda s, v: s._setExn(v))

    def handleException(self, (ty, value, tb), obj):
        """This is the main exception handling entry point.  When Python
           gets an exception it doesn't know how to handle, this method will
           be called.  It then saves the traceback and displays the main
           dialog asking the user what to do next.  Once this method is
           called, there's no good way to go back to what you were doing
           before.

           All arguments are passed in from the handler created by calling
           self.install().  This method should not usually be overridden by
           a subclass.
        """

        responseHash = {MAIN_RESPONSE_OK: self.runQuit,
                        MAIN_RESPONSE_DEBUG: self.runDebug,
                        MAIN_RESPONSE_SAVE: self.runSave}

        # Quit if we got an exception when running pdb.
        if isinstance(value, bdb.BdbQuit):
            sys.exit(self.exitcode)

        # Restore original exception handler.
        sys.excepthook = sys.__excepthook__

        self.preWriteHook((ty, value, tb), obj)

        # Save the exception to the filesystem first.
        self.exn = self.exnClass((ty, value, tb), self.conf)
        (fd, self.exnFile) = self.openFile()
        text = self.exn.write(obj, fd)
        fd.close()

        self.postWriteHook((ty, value, tb), obj)

        # Run initial UI screen, asking whether to save/debug/quit.
        while True:
            win = self.intf.mainExceptionWindow(text, self.exnFile)
            if not win:
                self.runQuit((ty, value, tb))

            win.run()
            rc = win.getrc()

            try:
                responseHash[rc]((ty, value, tb))
            except KeyError:
                # This happens if (for example) the user hits Escape instead
                # of pressing a button.
                continue

        win.destroy()

    def preWriteHook(self, (ty, value, tb), obj):
        """Subclasses may supply a function with this name that will be
           called immediately before the traceback is written to disk in
           order to have any sort of special pre-write processing that needs
           to be done.

           (ty, value, tb) -- The Python objects created when a traceback
                              occurs.  These are passed in directly from
                              handleException.
           obj -- A Python object that may be dumped to a file when the
                  exception is saved.  This should be something like the top
                  level object in a program.
        """
        pass

    def postWriteHook(self, (ty, value, tb), obj):
        """Subclasses may supply a function with this name that will be
           called immediately after the traceback is written to disk, but
           immediately before the UI is run.  This is to provide a place for
           any special handling to happen once there is a file on disk.

           (ty, value, tb) -- The Python objects created when a traceback
                              occurs.  These are passed in directly from
                              handleException.
           obj -- A Python object that may be dumped to a file when the
                  exception is saved.  This should be something like the top
                  level object in a program.
        """
        pass

    def install(self, obj):
        """Install ourselves as the top level exception handler with Python.
           If this method is not called after an ExceptionHandler instance is
           created, none of the rest of this code will ever be called.

           obj -- A Python object that may be dumped to a file when the
                  exception is saved.  This should be something like the top
                  level object in a program.
        """
        sys.excepthook = lambda ty, value, tb: self.handleException((ty, value, tb), obj)

    def openFile(self):
        """Create a randomly named output file to write the exception dump to.
           This requires a programName be set in the Config instance.  The
           return value is a (file descriptor, path) pair.  The file must be
           closed by the caller when writing is done.  Subclasses should not
           override this method unless they know what they're doing.
        """
        import tempfile
        (fd, path) = tempfile.mkstemp("", "%s-tb-" % self.conf.programName, "/tmp")
        fo = os.fdopen(fd, "w")
        return (fo, path)

    ### Methods called by the primary exception handling dialog.

    def runQuit(self, (ty, value, tb)):
        """This method is called when the "Exit" button is clicked.  It may
           be overridden by a subclass, but the basic behavior of eventually
           quitting should be preserved.
        """
        sys.exit(self.exitcode)

    def runDebug(self, (ty, value, tb)):
        """This method is called when the "Debug" button is clicked.  It may
           be overridden by a subclass if specialized behavior is required to
           enter debug mode.
        """
        import pdb
        pdb.post_mortem(tb)
        os.kill(os.getpid(), signal.SIGKILL)

    def runSave(self, (ty, value, tb)):
        """This method is called when the "Save" button is clicked.  It may
           be overridden by a subclass, but that's going to be a lot of work.
        """
        responseHash = {0: self.saveToLocal,
                        1: self.saveToBugzilla,
                        2: self.saveToRemote}

        win = self.intf.saveExceptionWindow(self.exnFile, desc=self.exn.desc)
        if not win:
            self.runQuit((ty, value, tb))

        while True:
            win.run()
            rc = win.getrc()

            if rc == SAVE_RESPONSE_OK:
                try:
                    (choice, dest) = win.getDest()

                    if responseHash[choice](dest):
                        if choice != 1:
                            # because the bugzilla choice already displayed a
                            # dialog along those lines
                            self.intf.exitWindow(_("Dump Written"),
                                                 _("The error file has been successfully "
                                                   "written.  The program will now exit."))
                        self.runQuit((ty, value, tb))
                    else:
                        self.intf.messageWindow(_("Dump Not Written"),
                                                _("There was a problem writing the "
                                                  "error report."))
                except NoNetwork:
                    self.intf.messageWindow(_("No Network Available"),
                                            _("Cannot save a bug report since there is "
                                              "no active network device available."))
            elif rc == SAVE_RESPONSE_CANCEL:
                break

        win.destroy()

    ### Methods called by the secondary exception saving dialog.

    def saveToLocal(self, dest):
        """This method is called when the local disk option is selected.  It
           may be overridden by a subclass.  This method returns True/False
           depending on if saving worked.

           dest -- The full path of where the exception should be copied to.
        """
        import shutil

        try:
            shutil.copyfile(self.exnFile, "%s/%s" % (dest, os.path.basename(self.exnFile)))
            return True
        except:
            return False

    def saveToRemote(self, dest):
        """This method is called when the scp option is selected.  It may
           be overridden by a subclass.  This method returns True/False
           depending on if saving worked.

           dest -- A (user, password, host, path) tuple describing how and
                   where to connect.
        """

        # Have to have the network in order to use this method.
        if not hasActiveNetDev() and not self.intf.enableNetwork():
            raise NoNetwork

        from savers import copyExceptionToRemote
        return copyExceptionToRemote(self.conf, self.exnFile, self.exn, dest)

    def saveToBugzilla(self, dest):
        """This method is called when the bugzilla option is selected.  It
           may be overridden by a subclass.  This method returns True/False
           depending on if saving worked.

           dest -- A (user, password, description) tuple describing how to
                   connect.
        """

        # Have to have the network in order to use this method.
        if not hasActiveNetDev() and not self.intf.enableNetwork():
            raise NoNetwork

        from savers import saveToBugzilla
        return saveToBugzilla(self.conf, self.exnFile, self.exn, dest)
