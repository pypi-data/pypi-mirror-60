# Copyright (c) 2013 Qumulo, Inc.
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
from __future__ import unicode_literals

import warnings

import qumulo.lib.request as request

from qumulo.lib.qstr import qstr as str
from qumulo.rest.node_state import get_node_state

@request.request
def unconfigured(conninfo, credentials):
    warnings.warn(
        'This function has been deprecated in favor of '
            'node_state.get_node_state.',
        DeprecationWarning)

    state = get_node_state(conninfo, credentials).lookup('state')

    if state == 'UNCONFIGURED':
        # XXX sjelin: really we should be constructing a RestResponse who's
        # contents is 'null', but it probably doesn't matter. The important
        # thing is that we raise an error if and only if we're configured.
        return None
    else:
        raise request.RequestError(405, 'Method Not Allowed', None)

def fmt_unconfigured_nodes(unconfigured_nodes_response):
    '''
    @param unconfigured_nodes_response The result of list_unconfigured_nodes
    @return a string containing a pretty table of the given nodes.
    '''
    if not unconfigured_nodes_response.data.get('nodes'):
        return "No unconfigured nodes found."

    # Flatten the list of dicts (containing dicts) to a square array, with
    # column headers.
    flattened = [('LABEL', 'MODEL', 'VERSION', 'BUILD', 'UUID')] + [
        (
            node['label'],
            node['model_number'],
            node['node_version']['revision_id'],
            node['node_version']['build_id'],
            node['uuid']
        ) for node in unconfigured_nodes_response.data['nodes']]

    # Get the length of the longest value in each column
    max_widths = [ max([len(str(row[col])) for row in flattened])
        for col in range(len(flattened[0]))]

    # Print the table, with values in each column padded to the length of that
    # column's longest value.
    line_fmt = "{0:<{w[0]}} {1:<{w[1]}} {2:<{w[2]}} {3:<{w[3]}} {4:<{w[4]}}"
    return "\n".join([line_fmt.format(*r, w=max_widths) for r in flattened])

@request.request
def list_unconfigured_nodes(conninfo, credentials):
    method = "GET"
    uri = "/v1/unconfigured/nodes/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def add_node(conninfo, credentials, node_uuids=None):
    warnings.warn(
        'This function has been deprecated in favor of cluster.add_node.',
        DeprecationWarning)

    method = "POST"
    uri = "/v1/cluster/nodes/"

    req = {
        'node_uuids': list() if node_uuids is None else list(node_uuids)
    }

    return request.rest_request(conninfo, credentials, method, uri, body=req)
