import json
from threading import Lock
import netconf.util as ncutil
from lxml import etree as ET
from netconf import nsmap_update, server
from config import read_json_config_file

from notifications import Subscription
from notifications import PeriodicNotificationThread

from pymongo import MongoClient
from pymongo import MongoClient

import logging

logger = None

# TODO model namespace??
MODEL_NS = "urn:my-urn:my-model"

nsmap_update({'pfx': MODEL_NS, 'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push'})

class PublisherServer:
    def __init__(self, config_file='server_config.json'):
        
        """
        :param config_file: server config file path
        :param debug:
        """
        # read configuration
        cfg = read_json_config_file(config_file)
        
        # Set up logger
        global logger
        logger = logging.getLogger('publisher')
        logger.setLevel(logging.DEBUG)

        # create file handler which logs all messages
        fh = logging.FileHandler('publisher_debug.log')
        fh.setLevel(logging.DEBUG)

        ch_level = logging.DEBUG if cfg.debug else logging.INFO
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(ch_level)

        formatter = logging.Formatter('%(asctime)s %(name)s %(threadName)s %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        
        self.subscriptions = {}
        self.last_subscription_id = 0
        self.port = cfg.port
        self.debug = cfg.debug
        self._storage_file_lock = Lock()

        self.client = MongoClient(f"mongodb://{cfg.mongo_host}:{cfg.mongo_port}/?readPreference=primary&appname=netconf-publisher&ssl=false", serverSelectionTimeoutMS=2000)
        
        # Test mongoDB connection. Fails if could not connect to any mongodb server and raises an exception
        try:
            self.client.server_info()
        except Exception as e:
            logger.error(f"MongoDB error: {e}")
            raise e
        self.db = self.client[cfg.mongo_db]

        # Authentication
        #
        # There are two available authentication methods:
        #    1. User and password (used now), allowing only one user (no way to establish access rules)
        #    2. SSH authorized keys. A list of the allowed clients public keys
        auth_controller = server.SSHUserPassController(username=cfg.username, password=cfg.password)

        server.NetconfSSHServer(server_ctl=auth_controller,
                                server_methods=self,
                                port=cfg.port,
                                host_key=cfg.ssh_host_key_path,
                                debug=cfg.debug)

        logger.info(f"Server started on port {self.port}")


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

        logger.info("Received establish-subscription RPC")

        sub_type = None

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
            sub = Subscription(sid, sub_type, datastore, xpath_filter, interval=period,
                               raw=ET.tostring(rpc, pretty_print=True).decode('utf8'))
            self.subscriptions[sid] = sub

        # Generate response
        res_map = {None: 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'}

        # id tag containing the subscription id
        res = ET.Element('id', nsmap=res_map)
        res.text = str(sid)
        
        logger.debug(ET.tostring(rpc, pretty_print=True).decode('utf8'))
        logger.debug(ET.tostring(res, pretty_print=True).decode('utf8'))

        PeriodicNotificationThread(sub, self.db, session)

        return res

    def get_next_sub_id(self):
        self.last_subscription_id += 1
        return self.last_subscription_id
