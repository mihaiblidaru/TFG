#!/usr/bin/python3
from netconf.client import NetconfSSHSession
import time
from lxml import etree
from argparse import ArgumentParser
import lxml
from netconf import util
from netconf import nsmap_update

nsmap_update({'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push',
              'ds': 'urn:ietf:params:xml:ns:yang:ietf-datastores'})
              
class Parser(ArgumentParser):
    help_str = """Netconf client capable of yang push notifications."""

    def __init__(self, prog):
        super().__init__(prog, description=self.help_str)
        self.add_argument('-H', '--host', required=False, default="127.0.0.1", help="Netconf server host", type=str)
        self.add_argument('-p', '--port', required=False, default=830, help="Netconf server listening port", type=int)
        self.add_argument('-U', '--user', required=False, default="admin", help="Netconf username", type=str)
        self.add_argument('-P', '--password', required=False, default="admin", help="Netconf password", type=str)
        self.add_argument('-x', '--xpath', required=True, help="xpath filter")
        self.add_argument('-i', '--period', required=True, help="Time between notifications", type=int)

    def parse_argv(self):
        return vars(self.parse_args())

def main():
    parser = Parser(__file__)
    args = parser.parse_args()

    session = NetconfSSHSession(args.host, args.port, args.user, args.password)

    es_nsmap = {'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push'}
    root = lxml.etree.Element('establish-subscription', nsmap=es_nsmap,
                              attrib={'xmlns': 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'})

    datastore = util.leaf_elm('yp:datastore', 'ds:operational')
    root.append(datastore)

    datastore_xpath_filter = util.leaf_elm('yp:datastore-xpath-filter', args.xpath)

    root.append(datastore_xpath_filter)

    periodic = util.subelm(root, 'yp:periodic')
    period = util.leaf_elm("yp:period", args.period)
    periodic.append(period)

    res = session.send_rpc(root)

    while True:
        tree, notif, msg = session.get_notification()
        print(etree.tounicode(notif, pretty_print=True), end="\n\n")


if __name__ == "__main__":
    main()

