# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2019 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
List of named objects for Interface, Part, Net, Bus, Pin objects.
These lists are actually dictionaries so an object with a given name
can be accessed very quickly without searching through all the objects.
"""

from .utilities import to_list


class NamedList(dict):
    def __init__(self, *args, **kwargs):
        self.key_attrs = to_list(kwargs.pop("key_attr"))
        super().__init__(*args, **kwargs)

    def add(self, item):
        for key_attr in self.key_attrs:
            key = getattr(item, key_attr)
            if key in self:
                raise Exception("Duplicated key!")
            self[key] = item
        return self

    def sub(self, item):
        for key_attr in self.key_attrs:
            key = getattr(item, key_attr)
            del self[key]
        return self

    __iadd__ = add
    __isub__ = sub
