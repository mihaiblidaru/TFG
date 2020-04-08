from netconf.client import NetconfSSHSession
import time
from lxml import etree
session = NetconfSSHSession('192.168.0.2', 55555, 'admin','admin')

rpc = '<establish-subscription xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push" xmlns="urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications"><yp:datastore>ds:operational</yp:datastore><yp:datastore-xpath-filter>/system/contact</yp:datastore-xpath-filter><yp:periodic><yp:period>3</yp:period></yp:periodic></establish-subscription>'
res = session.send_rpc(rpc)


while True:
    tree, notif, msg = session.get_notification()
    print(etree.tounicode(notif, pretty_print=True), end="\n\n")