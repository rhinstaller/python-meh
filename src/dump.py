#
# dump.py - general exception formatting and saving
#
# Copyright (C) 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009  Red Hat, Inc.
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
# Author(s): Matt Wilson <msw@redhat.com>
#            Erik Troan <ewt@redhat.com>
#            Chris Lumens <clumens@redhat.com>
#
import inspect
from string import joinfields
import os
import traceback
import types

class ExceptionDump(object):
    """This class represents a traceback and contains several useful methods
       for manipulating a traceback.  In general, clients should not have to
       use this class.  It is mainly for internal use.
    """
    def __init__(self, (ty, value, stack), configObj):
        """Create a new ExceptionDump instance.  Instance attributes:

           (type, value, stack) -- These are the values provided by python
                                   when an exception is generated, and are
                                   what ExceptionDump wraps to make more
                                   useful.
           conf                 -- An instance of the Config object.
        """

        if inspect.istraceback(stack):
            stack = inspect.getinnerframes(stack)

        self.conf = configObj
        self.stack = stack
        self.type = ty
        self.value = value

        self._dumpHash = {}

    @property
    def desc(self):
        # The description is a single line of text that should be used anywhere
        # the bug needs to quickly be summarized.  The most obvious example of
        # this is when saving to bugzilla.  We can populate the UI with this
        # string so the user doesn't need to come up with one.
        if self.type and self.value:
            return traceback.format_exception_only(self.type, self.value)[0].strip()
        else:
            return ""

    def __str__(self):
        lst = self._format_stack()

        lst.insert(0, "%s %s exception report\n" % (self.conf.programName, self.conf.programVersion))
        lst.insert(1, "Traceback (most recent call last):\n")

        if self.type is not None and self.value is not None:
            lst.extend(traceback.format_exception_only(self.type, self.value))

        return joinfields(lst, "")

    def _format_stack(self):
        frames = []
        for (frame, fn, lineno, func, ctx, idx) in self.stack:
            if type(ctx) == type([]):
                code = "".join(ctx)
            else:
                code = ctx

            frames.append((fn, lineno, func, code))

        return traceback.format_list(frames)

    # Create a string representation of a class and write it to fd.  This
    # method will recursively handle all attributes of the base given class.
    def _dumpClass(self, instance, fd, level=0, parentkey="", skipList=[]):
        # protect from loops
        try:
            if not self._dumpHash.has_key(instance):
                self._dumpHash[instance] = None
            else:
                fd.write("Already dumped\n")
                return
        except TypeError:
            fd.write("Cannot dump object\n")
            return

        if (instance.__class__.__dict__.has_key("__str__") or
            instance.__class__.__dict__.has_key("__repr__")):
            fd.write("%s\n" % (instance,))
            return
        fd.write("%s instance, containing members:\n" %
                 (instance.__class__.__name__))
        pad = ' ' * ((level) * 2)

        for key, value in instance.__dict__.items():
            if key.startswith("_%s__" % instance.__class__.__name__):
                continue

            if parentkey != "":
                curkey = parentkey + "." + key
            else:
                curkey = key

            # Don't dump objects that are in our skip list, though ones that are
            # None are probably okay.
            if eval("instance.%s is not None" % key) and \
               eval("id(instance.%s)" % key) in skipList:
                continue

            if type(value) == types.ListType:
                fd.write("%s%s: [" % (pad, curkey))
                first = 1
                for item in value:
                    if not first:
                        fd.write(", ")
                    else:
                        first = 0
                    if type(item) == types.InstanceType:
                        self._dumpClass(item, fd, level + 1, skipList=skipList)
                    else:
                        fd.write("%s" % (item,))
                fd.write("]\n")
            elif type(value) == types.DictType:
                fd.write("%s%s: {" % (pad, curkey))
                first = 1
                for k, v in value.items():
                    if not first:
                        fd.write(", ")
                    else:
                        first = 0
                    if type(k) == types.StringType:
                        fd.write("'%s': " % (k,))
                    else:
                        fd.write("%s: " % (k,))
                    if type(v) == types.InstanceType:
                        self._dumpClass(v, fd, level + 1, parentkey = curkey, skipList=skipList)
                    else:
                        fd.write("%s" % (v,))
                fd.write("}\n")
            elif type(value) == types.InstanceType:
                fd.write("%s%s: " % (pad, curkey))
                self._dumpClass(value, fd, level + 1, parentkey=curkey, skipList=skipList)
            else:
                fd.write("%s%s: %s\n" % (pad, curkey, value))

    def dump(self, fd, obj):
        """Dump the local variables and all attributes of a given object to an
           open file descriptor.  The lists of files and attrs to ignore are
           all taken from a Config object instance provided when the
           ExceptionDump class was created.

           fd  -- An open file descriptor to write everything to.
           obj -- Any Python object.  This object will have all its attributes
                  written out, except for those mentioned in the attrSkipList.
        """
        idSkipList = []

        # Catch attributes that do not exist at the time we do the exception dump
        # and ignore them.
        for k in self.conf.attrSkipList:
            try:
                eval("idSkipList.append(id(%s))" % k)
            except:
                pass

        # Write local variables to the given file descriptor, ignoring any of
        # the local skips.
        if self.stack:
            frame = self.stack[-1][0]
            fd.write ("\nLocal variables in innermost frame:\n")
            try:
                for (key, value) in frame.f_locals.items():
                    loweredKey = key.lower()
                    if len(filter(lambda s: loweredKey.find(s) != -1, self.conf.localSkipList)) > 0:
                        continue

                    fd.write ("%s: %s\n" % (key, value))
            except:
                pass

        # And now dump the object's attributes.
        try:
            fd.write("\n\n")
            self._dumpClass(obj, fd, skipList=idSkipList)
        except:
            fd.write("\nException occurred during state dump:\n")
            traceback.print_exc(None, fd)

        # And finally, write a bunch of files into the dump too.
        for fn in self.conf.fileList:
            try:
                f = open(fn, 'r')
                line = "\n\n%s:\n" % (fn,)
                while line:
                    fd.write(line)
                    line = f.readline()
                f.close()
            except IOError:
                pass
            except:
                fd.write("\nException occurred during %s file copy:\n" % (fn,))
                traceback.print_exc(None, fd)

    @property
    def hash(self):
        """Create a hash for this traceback object.  This is most suitable for
           searching bug filing systems for duplicates.  The hash is composed
           of the basename of each file in the stack, the method names, and
           the bit of code.  Line numbers and the actual exception message
           itself are left out.
        """
        import hashlib
        s = ""

        for (file, lineno, func, text) in [f[1:5] for f in self.stack]:
            if type(text) == type([]):
                text = "".join(text)
            s += "%s %s %s\n" % (os.path.basename(file), func, text)

        return hashlib.sha256(s).hexdigest()

    def write(self, obj, fd):
        """Write the traceback and a text representation of an object to an
           open file descriptor.

           fd  -- An open file descriptor to write everything to.
           obj -- Any Python object.  This object will have all its attributes
                  written out, except for those mentioned in the attrSkipList.
        """
        ret = str(self)
        fd.write(ret)
        self.dump(fd, obj)
        return ret

class ReverseExceptionDump(ExceptionDump):
    """This class provides an alternate representation of an exception.  In
       this representation, the traceback is printed with the most recent call
       at the top of the stack, and the most generic call at the bottom.  Note
       that this order does not affect the hash at all.
    """
    def __str__(self):
        lst = self._format_stack()
        lst.reverse()

        lst.insert(0, "%s %s exception report\n" % (self.conf.programName, self.conf.programVersion))
        lst.insert(1, "Traceback (most recent call first):\n")

        if self.type is not None and self.value is not None:
            lst.extend(traceback.format_exception_only(self.type, self.value))

        return joinfields(lst, "")
