# -*- coding: utf-8 eval: (yapf-mode 1) -*-
#
# January 22 2018, Christian E. Hopps <chopps@gmail.com>
#
# Copyright (c) 2018, Deutsche Telekom AG.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import absolute_import, division, unicode_literals, print_function, nested_scopes
import getpass
import logging
from lxml import etree
import netconf.client
from mockserver import init_mock_server
from testutil import xml_eq

logger = logging.getLogger(__name__)
NC_PORT = None
NC_DEBUG = False


def setup_module(unused_module):
    global NC_PORT
    NC_PORT = init_mock_server()


def test_get_config():
    session = netconf.client.NetconfSSHSession("127.0.0.1",
                                               username=getpass.getuser(),
                                               password="admin",
                                               port=NC_PORT,
                                               debug=NC_DEBUG)
    result = session.get_config()
    cmptree = etree.fromstring("""
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <t:interfaces xmlns:t="urn:test:mock">
    <t:interface>
      <t:name>Ethernet0/0</t:name>
      <t:shutdown>true</t:shutdown>
    </t:interface>
    <t:interface>
      <t:name>Ethernet0/1</t:name>
      <t:shutdown>false</t:shutdown>
    </t:interface>
    <t:interface>
      <t:name>FastEthernet1/0</t:name>
      <t:shutdown>false</t:shutdown>
    </t:interface>
    <t:interface>
      <t:name>FastEthernet1/1</t:name>
      <t:shutdown>false</t:shutdown>
      <t:name>GigabitEthernet2/0</t:name>
      <t:shutdown>false</t:shutdown>
    </t:interface>
  </t:interfaces>
</nc:data>
    """)
    assert (xml_eq(result, cmptree))


def test_get():
    session = netconf.client.NetconfSSHSession("127.0.0.1",
                                               username=getpass.getuser(),
                                               password="admin",
                                               port=NC_PORT,
                                               debug=NC_DEBUG)
    result = session.get()
    cmptree = etree.fromstring("""
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <t:interfaces xmlns:t="urn:test:mock">
    <t:interface>
      <t:name>AutoInterface0/0</t:name>
      <t:shutdown>false</t:shutdown>
      <t:state>up</t:state>
    </t:interface>
    <t:interface>
      <t:name>Ethernet0/0</t:name>
      <t:shutdown>true</t:shutdown>
      <t:state>down</t:state>
    </t:interface>
    <t:interface>
      <t:name>Ethernet0/1</t:name>
      <t:shutdown>false</t:shutdown>
      <t:state>down</t:state>
    </t:interface>
    <t:interface>
      <t:name>FastEthernet1/0</t:name>
      <t:shutdown>false</t:shutdown>
      <t:state>up</t:state>
    </t:interface>
    <t:interface>
      <t:name>FastEthernet1/1</t:name>
      <t:shutdown>false</t:shutdown>
      <t:state>down</t:state>
    </t:interface>
  </t:interfaces>
</nc:data>
    """)
    assert (xml_eq(result, cmptree))


__author__ = 'Christian E. Hopps'
__date__ = 'January 22 2018'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
