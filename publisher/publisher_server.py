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
from lxml import etree as ET

# TODO model namespace??
MODEL_NS = "urn:my-urn:my-model"

nsmap_update({'pfx': MODEL_NS, 'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push',
              None: 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notification'})

class PublisherServer:
    def __init__(self, user, pw, port=55555, storage_file='subscriptions.json', debug=False):
        self.storage_file = storage_file
        self.subscriptions = []
        self.port = port
        self.debug=debug
        self.load_subscriptions_file()
        self._storage_file_lock = Lock()
        server_ctl = server.SSHUserPassController(
            username=user, password=user)
        server.NetconfSSHServer(server_ctl=server_ctl,
                                            server_methods=self,
                                            port=55555,
                                            host_key="ssh/id_rsa",
                                            debug=True)


    def nc_append_capabilities(self, caps):
        # TODO netconf server capabilities
        ncutil.subelm(caps, "capability").text = MODEL_NS


    def rpc_establish_subscription(self, session, rpc, *params):
        """ Source https://tools.ietf.org/id/draft-ietf-netconf-yang-push-19.html 
            +---x establish-subscription
        |  +---w input
        |  |  ...
        |  |  +---w (target)
        |  |  |  +--:(stream)
        |  |  |  |  ...
        |  |  |  +--:(yp:datastore)
        |  |  |     +---w yp:datastore                   identityref
        |  |  |     +---w (yp:selection-filter)?
        |  |  |        +--:(yp:by-reference)
        |  |  |        |  +---w yp:selection-filter-ref        
        |  |  |        |          selection-filter-ref
        |  |  |        +--:(yp:within-subscription)
        |  |  |           +---w (yp:filter-spec)?
        |  |  |              +--:(yp:datastore-subtree-filter)
        |  |  |              |  +---w yp:datastore-subtree-filter?   
        |  |  |              |          <anydata> {sn:subtree}?
        |  |  |              +--:(yp:datastore-xpath-filter)
        |  |  |                 +---w yp:datastore-xpath-filter?     
        |  |  |                         yang:xpath1.0 {sn:xpath}?
        |  |  | ...
        |  |  +---w (yp:update-trigger)
        |  |     +--:(yp:periodic)
        |  |     |  +---w yp:periodic!
        |  |     |     +---w yp:period         yang:timeticks
        |  |     |     +---w yp:anchor-time?   yang:date-and-time
        |  |     +--:(yp:on-change) {on-change}?
        |  |        +---w yp:on-change!
        |  |           +---w yp:dampening-period?   yang:timeticks
        |  |           +---w yp:sync-on-start?      boolean
        |  |           +---w yp:excluded-change*    change-type
        |  +--ro output
        |     +--ro id                            subscription-id
        |     +--ro replay-start-time-revision?   yang:date-and-time 
        |             {replay}?
        """
        # We have recieved an establish-subscription rpc
        # TODO validate more fields from the RPC 

        sub_type = None

        # TODO check if there is another way to get the client ip address
        dest = session.pkt_stream.stream.transport.sock.getpeername()[0]

        root = rpc[0]
        nsmap = rpc[0].nsmap

        periodic_elm = root.find('yp:periodic', nsmap)
        on_change_elm = root.find('yp:on-change', nsmap)
        datastore_elm = root.find('yp:datastore', nsmap)
        datastore_xpath_filter_elm = root.find('yp:datastore-xpath-filter', nsmap)

        if periodic_elm is not None:
            period_elm = periodic_elm.find('yp:period', nsmap)
            period = int(period_elm.text)
            sub_type = Subscription.PERIODIC
        elif on_change_elm is not None:
            sub_type = Subscription.ON_CHANGE
        else:
            # Malformed request
            return ncutil.leaf_elm('error', 'Neither periodic nor on change found in establish-subscription request')        

        xpath_filter = datastore_xpath_filter_elm.text
        datastore = datastore_elm.text

        if sub_type == Subscription.PERIODIC:
            sid = self.get_next_sub_id()
            sub = Subscription(sid, sub_type, datastore,  xpath_filter, dest, interval=period, raw=ET.tostring(rpc, pretty_print=True).decode('utf8'))
            self.add_subcription(sub)


        # Generate response
        res_map = {None:'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'}

        # id tag containing the subscription id
        res = ET.Element('id', nsmap=res_map)
        res.text = str(sid)
        if self.debug:
            print(ET.tostring(rpc, pretty_print=True).decode('utf8'))
        if self.debug:
            print(ET.tostring(res, pretty_print=True).decode('utf8'))

        return res


    ######################################################################
    ##############     Subscription persistence layer        #############
    ######################################################################
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
            res = list(map(lambda  sub: sub.to_dict(), self.subscriptions))
            json.dump(res, fp, indent=4)

        # Release it when the file is closed
        self._storage_file_lock.release()

    def get_next_sub_id(self):
        sid = 1
        if self.subscriptions:
            sid = max(map(lambda x: x.sid, self.subscriptions)) + 1

        return sid

    def add_subcription(self, sub):
        self.subscriptions.append(sub)
        self.serialize_subscription_file()
    
    ######################################################################
    ##############     END Subscription persistence layer    #############
    ######################################################################
