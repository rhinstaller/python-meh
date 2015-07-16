#
# Copyright (C) 2013  Red Hat, Inc.
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
# Author: Vratislav Podzimek <vpodzime@redhat.com>
#
#

import sys
PY = int(sys.version.split('.')[0])

"""
This module provides a SafeStr class.

@see: SafeStr

"""

class SafeStr(str):
    """
    String class that has a modified __add__ method so that ascii strings,
    binary data represented as a byte string and unicode objects can be
    safely appended to it (not causing traceback). BINARY DATA IS OMITTED.

    """

    def __add__(self, other):

        if PY > 2:
            return SafeStr(str.__add__(self, str(other)))

        if not (isinstance(other, str) or isinstance(other, unicode)):    # pylint: disable=undefined-variable
            if hasattr(other, "__str__"):
                other = other.__str__()
            else:
                other = "OMITTED OBJECT WITHOUT __str__ METHOD"

        if isinstance(other, unicode):    # pylint: disable=undefined-variable
            ret = SafeStr(str.__add__(self, other.encode("utf-8")))
        else:
            try:
                # try to decode which doesn't cause traceback for utf-8 encoded
                # non-ascii string and ascii string
                other.decode("utf-8")
                ret = SafeStr(str.__add__(self, other))
            except UnicodeDecodeError:
                # binary data, get the representation used by Python for
                # non-ascii bytes

                # hex(255) returns "0xff", we want "\xff"
                other_hexa = (hex(ord(char)) for char in other)
                other_backslashed = (hex_num.replace("0x", "\\x")
                                     for hex_num in other_hexa)
                other_repr = "".join(other_backslashed)

                ret = SafeStr(str.__add__(self, other_repr))

        return ret
