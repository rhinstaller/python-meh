#
# __init__.py - Basic stuff for exception handling
#
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

# These constants represent the return values of buttons on the initial
# exception handling dialog - the dialog that first pops up when an
# exception is hit.
MAIN_RESPONSE_DEBUG = 0
MAIN_RESPONSE_SAVE = 1
MAIN_RESPONSE_OK = 2

# And these constants represent the return values of buttons on the exception
# saving dialog.
SAVE_RESPONSE_OK = 0
SAVE_RESPONSE_CANCEL = 1

class Config(object):
    """Hold configuration info useful throughout the exception handling
       classes.  This prevents having to pass a bunch of arguments to a
       bunch of different functions.  A Config instance must be created
       before creating an ExceptionHandler instance.
    """
    def __init__(self, *args, **kwargs):
        """Create a new Config instance.  Arguments may be passed in to
           set any of the configuration values.  Unknown arguments will
           be ignored.  Instance attributes:

           attrSkipList   -- A list of strings.  When handling a traceback,
                             any attributes found with the same name as an
                             element of this list will not be written to
                             the dump.  This is to prevent writing potentially
                             sensitive information like passwords.  The names
                             must be given without the leading name of the
                             object passed to handler.install().  For instance,
                             if handler.install() gets an Anaconda instance
                             with the name "anaconda" and you want to skip
                             anaconda.id.rootPassword, "id.rootPassword" should
                             be listed in attrSkipList.
           fileList       -- A list of files to find on the system and add
                             to the traceback dump.
           localSkipList  -- A list of strings.  When handling a traceback,
                             any local variables found with the same name as
                             an element of this list will not be written to
                             the dump.  This is subtely different from
                             attrSkipList.
           programName    -- The name of the erroring program.
           programVersion -- The version number of the erroring program.
                             Both programName and programVersion are used
                             throughout the exception handler, so must be
                             set.
        """
        self.attrSkipList = []
        self.fileList = []
        self.localSkipList = []
        self.programName = None
        self.programVersion = None

        # Override the defaults set above with whatever's passed in as an
        # argument.  Unknown arguments get thrown away.
        for (key, val) in kwargs.iteritems():
            if self.__dict__.has_key(key):
                self.__dict__[key] = val

        # Make sure required things are set.
        if not self.programName:
            raise ValueError("programName must be set.")

        if not self.programVersion:
            raise ValueError("programVersion must be set.")
