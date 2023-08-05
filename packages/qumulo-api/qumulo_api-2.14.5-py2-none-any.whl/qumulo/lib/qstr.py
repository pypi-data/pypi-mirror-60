# Copyright (c) 2019 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from __future__ import absolute_import
from future.types.newstr import BaseNewStr, newstr
from future.utils import PY2, with_metaclass

from builtins import bytes, isinstance
from builtins import str as newstr

class BaseQstr(BaseNewStr):
    def __instancecheck__(cls, instance):
        return isinstance(instance, newstr)

# `newstr` has some abstract methods (very strange)
# pylint: disable=abstract-method
class _qstr(with_metaclass(BaseQstr, newstr)):
    '''
    A tweak on future's `newstr` which decodes unicode more reliably.

    There are two specific ways in which this differs from future's `newstr`:

    1) If you do not specify an encoding, `qstr` will use UTF-8. `newstr` uses
       `sys.getdefaultencoding()` by default, which is typically `'ascii'` in
       python 2 (though it can be set to something else by your `site.py`).
       Technically, `newstr` is correct that python 3's `str` defaults to
       `sys.getdefaultencoding()`. However, `sys.getdefaultencoding()` always
       returns `'UTF-8'` in python 3 (as of 3.4.1, though it can still be
       changed with some hacks). So hardcoding the default to `'UTF-8'` is more
       accurate to how `str` actually behaves in python 3.
    2) If you supply `qstr` with an encoding, it will always use that encoding
       to decode from bytes to unicode. `newstr` only uses the encoding for
       instances of python 2's `str` or its `newbytes` type.

    These tweaks are important because it is very common for a python 2 `str` to
    be passed into `newstr` without specifying an encoding. For example:

        from builtins import str
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('--name', type=str)
        arser.parse_args()

    Because `sys.argv` is an array of `str` instead of `unicode`, and `type=str`
    refers to future's `newstr`, this will cause a `UnicodeDecodeError` in
    python 2 (in most environments) if a non-ASCII character was supplied.
    '''

    def __new__(cls, s='', encoding='UTF-8', errors='strict'):
        # If decoding from unicode is required, ensure that we've converted `s`
        # to `bytes` before passing on to `newstr.__new__`, so that it uses the
        # encoding we supply it when decoding `s.__str__`.
        if not (isinstance(s, (newstr, bytes)) or hasattr(s, '__unicode__')):
            s = s.__str__()

        return super(_qstr, cls).__new__(
            cls, s, encoding=encoding, errors=errors)

# In python 3, we export the builtin string type instead of our implementation.`
qstr = _qstr if PY2 else str
