# Copyright (C) 2008  Red Hat, Inc.
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
from filer import *
import os
import pty
import rpmUtils.arch
import xmlrpclib

import gettext
_ = lambda x: gettext.ldgettext("python-meh", x)

def saveToBugzilla(conf, exnFile, exn, (user, password, summary)):
    def withBugzillaDo(bz, fn):
        try:
            retval = fn(bz)
            return retval
        except CommunicationError, e:
            msg = _("Your bug could not be filed due to the following error "
                    "when communicating with bugzilla:\n\n%s" % str(e))
        except (TypeError, ValueError), e:
            msg = _("Your bug could not be filed due to bad information in "
                    "the bug fields.  This is most likely an error in "
                    "the bug filing program:\n\n%s" % str(e))

        conf._intf.messageWindow(_("Unable To File Bug"), msg)
        return None

    filer = conf.bugFiler

    if not filer or not filer.supportsFiling() or not filer.bugUrl:
        conf._intf.messageWindow(_("Bug Filing Not Supported"),
            _("Your distribution does not provide a "
              "supported bug filing system, so you "
              "cannot save your exception this way."))
        return False

    if user.strip() == "" or password.strip() == "" or summary.strip() == "":
        conf._intf.messageWindow(_("Invalid Bug Information"),
            _("Please provide a valid username, "
              "password, and short bug description."))
        return False

    try:
        withBugzillaDo(filer, lambda b: b.login(user, password))
    except LoginError:
        conf._intf.messageWindow(_("Unable To Login"),
            _("There was an error logging into %s "
              "using the provided username and "
              "password.") % filer.displayUrl)
        return False

    # Are there any existing bugs with this hash value?  If so we will just
    # add this traceback to the bug report and put the reporter on the CC
    # list.  Otherwise, we need to create a new bug.
    wb = "%s_trace_hash:%s" % (exn.programName, exn.hash)
    buglist = withBugzillaDo(filer, lambda b: b.query({'status_whiteboard': wb,
                                                       'status_whiteboard_type':'allwordssubstr',
                                                       'bug_status': []}))
    if buglist is None:
        return False

    if len(buglist) == 0:
        bug = withBugzillaDo(filer, lambda b: b.createbug(product=filer.getproduct(),
                                       component=exn.programName,
                                       version=filer.getversion(),
                                       platform=rpmUtils.arch.getBaseArch(),
                                       bug_severity="medium",
                                       priority="medium",
                                       op_sys="Linux",
                                       bug_file_loc="http://",
                                       summary=summary,
                                       comment="The following was filed automatically by %s:\n%s" % (exn.programName, str(exn)),
                                       status_whiteboard=wb))
        if bug is None:
            return False

        withBugzillaDo(bug, lambda b: b.attachfile(exnFile,
                               "Attached traceback automatically from %s." % exn.programName,
                               contenttype="text/plain", filename=os.path.basename(exnFile)))

        # Tell the user we created a new bug for them and that they should
        # go add a descriptive comment.
        conf._intf.exitWindow(_("Bug Created"),
            _("A new bug has been created with your traceback attached. "
              "Please add additional information such as what you were doing "
              "when you encountered the bug, screenshots, and whatever else "
              "is appropriate to the following bug:\n\n%s/%s") % (filer.displayUrl, bug.id()))
        return True
    else:
        bug = buglist[0]
        withBugzillaDo(bug, lambda b: b.attachfile(exnFile,
                               "Attached traceback automatically from %s." % exn.programName,
                               contenttype="text/plain", filename=os.path.basename(exnFile)))
        withBugzillaDo(bug, lambda b: b.addCC(user))

        # Tell the user which bug they've been CC'd on and that they should
        # go add a descriptive comment.
        conf._intf.exitWindow(_("Bug Updated"),
            _("A bug with your information already exists.  Your account has "
              "been added to the CC list and your traceback added as a "
              "comment.  Please add additional descriptive information to the "
              "following bug:\n\n%s/%s") % (filer.displayUrl, bug.id()))
        return True

def scpAuthenticate(master, childpid, password):
    while True:
        # Read up to password prompt.  Propagate OSError exceptions, which
        # can occur for anything that causes scp to immediately die (bad
        # hostname, host down, etc.)
        buf = os.read(master, 4096)
        if buf.lower().find("password: ") != -1:
            os.write(master, password+"\n")
            # read the space and newline that get echoed back
            os.read(master, 2)
            break

    while True:
        buf = ""
        try:
            buf = os.read(master, 4096)
        except (OSError, EOFError):
            break

    (pid, childstatus) = os.waitpid (childpid, 0)
    return childstatus

def copyExceptionToRemote(conf, srcFile, exn, (user, password, host, path)):
    if host.find(":") != -1:
        (host, port) = host.split(":")

        # Try to convert the port to an integer just as a check to see
        # if it's a valid port number.  If not, they'll get a chance to
        # correct the information when scp fails.
        try:
            int(port)
            portArgs = ["-P", port]
        except ValueError:
            portArgs = []
    else:
        portArgs = []

    # Fork ssh into its own pty
    (childpid, master) = pty.fork()
    if childpid < 0:
        raise RuntimeError("Could not fork process to run scp")
    elif childpid == 0:
        # child process - run scp
        args = ["scp", "-oNumberOfPasswordPrompts=1",
                "-oStrictHostKeyChecking=no"] + portArgs + \
               [srcFile, "%s@%s:%s" % (user, host, path)]
        os.execvp("scp", args)

    # parent process
    try:
        childstatus = scpAuthenticate(master, childpid, password)
    except OSError:
        return False

    os.close(master)

    if os.WIFEXITED(childstatus) and os.WEXITSTATUS(childstatus) == 0:
        return True
    else:
        return False
