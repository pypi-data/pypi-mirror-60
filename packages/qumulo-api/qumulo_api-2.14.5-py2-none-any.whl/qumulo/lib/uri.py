# Copyright (c) 2012 Qumulo, Inc.
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

from __future__ import absolute_import, unicode_literals
from future import standard_library
standard_library.install_aliases()

# pylint: disable=import-error
import urllib.parse as urllib

from qumulo.lib.qstr import qstr as str

class UriBuilder(object):
    '''
    Builds a URI, taking care of URI escaping and ensuring a well-formatted
    URI. Currently does not support adding a fragment to the end of a URI
    (e.g. #!hashbang).
    '''
    def __init__(self, scheme=None, hostname=None, port=None, username=None,
                 password=None, path=None, rstrip_slash=True):
        # Port is not allowed without a hostname
        assert (port and hostname) or (not hostname)

        # Username is not allowed without a hostname
        assert (username and hostname) or (not username)

        # Password is not allowed without a username
        assert (password and username) or (not password)

        self._scheme = self._unicode_sanitize(scheme)
        self._hostname = self._unicode_sanitize(hostname)
        self._port = self._unicode_sanitize(port)
        self._username = self._unicode_sanitize(username)
        self._password = self._unicode_sanitize(password)
        self._path = path or ''
        if rstrip_slash:
            self._path = path.rstrip('/')
            if not self._path.startswith('/'):
                self._path = '/' + self._path
        self._query_params = []
        self._fragment = ""

    def add_path_component(self, component, append_slash=False):
        '''
        Adds a single path component to the URI. Any characters not in the
        unreserved set, including '/', will be escaped.
        '''
        component = self._unicode_sanitize(component)

        # Completely URI encode the component, even the '/' characters
        self._path = str(u"%s/%s") % (
             self._path, urllib.quote(str(component) ,''))
        if append_slash:
            self.append_slash()
        return self

    def append_slash(self):
        self._path += '/'
        return self

    def add_query_param(self, name, value=None):
        '''
        Adds a query parameter with an optional value to the query string. Any
        characters not in the reserved set will be escaped. Spaces will be
        escaped with '+' characters
        '''
        name = self._unicode_sanitize(name)
        value = self._unicode_sanitize(value)

        if value is not None:
            self._query_params.append(
                "%s=%s" % (urllib.quote(name, ''),
                           urllib.quote(str(value), '')))
        else:
            self._query_params.append(urllib.quote_plus(name))

        return self

    def __str__(self):
        # The urlunsplit from future requires all arguments to be the same
        # type, either str or unicode.  Here we force them all to be python3
        # compatible unicode strings

        # Consider an empty path to be the root for string-printing purposes
        path = str("/") if not self._path else str(self._path)
        scheme = str() if not self._scheme else self._scheme
        netloc = str() if not self._netloc() else self._netloc()
        params = str('&'.join(list(map(str, self._query_params))))

        return urllib.urlunsplit((scheme, netloc, path, params, None))

    @staticmethod
    def _unicode_sanitize(param):
        if isinstance(param, (str, bytes)):
            return str(param)
        return param

    def _netloc(self):
        netloc = ""
        if self._hostname:
            if self._username:
                password_part = "" if not self._password else (
                    ":%s" % self._password)
                netloc = "%s%s@" % (self._username, password_part)

            if self._port:
                port_part = ":%s" % str(self._port)
            else:
                port_part = ""
            netloc += "%s%s" % (self._hostname, port_part)

        return netloc
