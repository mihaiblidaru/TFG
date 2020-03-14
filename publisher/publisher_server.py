from netconf import nsmap_update, server
import netconf.util as ncutil
from time import sleep
from netconf import util
from lxml import etree
import getpass
from netconf.server import NetconfServerSession
import json
from subscription import Subscription
from threading import Lock

MODEL_NS = "urn:my-urn:my-model"

nsmap_update({'pfx': MODEL_NS, 'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push',
              'sn': 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notification'})


class PublisherServer (object):
    def __init__(self, user, pw, storage_file='subscriptions.json'):
        self.storage_file = storage_file
        self.subscriptions = []
        self.load_subscriptions_file()
        self._storage_file_lock = Lock()
        server_ctl = server.SSHUserPassController(
            username=user, password=user)
        nc_server = server.NetconfSSHServer(server_ctl=server_ctl,
                                            server_methods=self,
                                            port=55555,
                                            host_key="ssh/id_rsa",
                                            debug=True)

    def load_subscriptions_file(self):
        try:
            with open(self.storage_file) as fp:
                _subs = json.load(fp)
                for _sub in _subs:
                    self.subscriptions.append(Subscription.from_dict(_sub))
        except:
            self.subscriptions = []

    def serialize_subscription_file(self):
        # Aquire lock over file
        self._storage_file_lock.acquire()

        with open(self.storage_file, 'w') as fp:
            res = []

            for sub in self.subscriptions:
                res.append(sub.to_dict())

            json.dump(res, fp, indent=4)

        # Release it when the file is closed
        self._storage_file_lock.release()

    def add_subcription(self, sub):
        self.subscriptions.append(sub)
        self.serialize_subscription_file()

    def nc_append_capabilities(self, caps):
        ncutil.subelm(caps, "capability").text = MODEL_NS

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):
        return util.elm("nc:ok")

    def rpc_get(self, session, rpc, *params):
        return util.elm("nc:ok")

    def get_next_sub_id(self):
        sid = 1
        if self.subscriptions:
            sid = max(map(lambda x: x.sid, self.subscriptions)) + 1

        return sid

    def rpc_establish_subscription(self, session, rpc, *params):
        # We have recieved an establish-subscription rpc, now
        # we have to check if it is well formed

        stype = None

        dest = session.pkt_stream.stream.transport.sock.getpeername()[0]

        for p in params:
            if p.tag.endswith('datastore-xpath-filter'):
                data = p.text.strip()
            if p.tag.endswith('periodic'):
                stype = Subscription.PERIODIC
                for ch in p.getchildren():
                    if ch.tag.endswith("period"):
                        interval = int(ch.text)

        if stype == Subscription.PERIODIC:
            sid = self.get_next_sub_id()
            sub = Subscription(sid, stype, data, dest, interval=interval)
            self.add_subcription(sub)

        print(sub)

        return util.leaf_elm("sn:id", sid)
