import os
from threading import Lock
from typing import Optional
import netconf.util as ncutil
from lxml import etree
from netconf import nsmap_update, server
import config as cfg

from notifications import Subscription
from notifications import PeriodicNotificationThread


from datasource import MongoDataSource
import logging

logger: Optional[logging.Logger] = None

# TODO model namespace??
MODEL_NS = "urn:my-urn:my-model"

nsmap_update(
    {'pfx': MODEL_NS,
     'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push'})


class PublisherServer:
    def __init__(self, config_file=''):
        """
        :param config_file: server config file path
        """

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

        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(threadName)s %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        self.subscriptions = {}
        self.last_subscription_id = 0
        self.port = cfg.port
        self.debug = cfg.debug
        self._storage_file_lock = Lock()


        self.datasource = None 

        
        try:
            self.datasource = MongoDataSource(cfg.mongo_host, cfg.mongo_port, cfg.mongo_db, cfg.mongo_collection)
        except Exception as e:
            logger.error(f"MongoDB error: {e}")
            raise e

        if not os.path.isabs(cfg.ssh_host_key_path):
            cfg.ssh_host_key_path = os.path.join(
                os.path.dirname(config_file), cfg.ssh_host_key_path)

        # Authentication
        #
        # There are two available authentication methods:
        #    1. User and password (used now), allowing only one user (no way to establish access rules)
        #    2. SSH authorized keys. A list of the allowed clients public keys
        auth_controller = server.SSHUserPassController(
            username=cfg.username, password=cfg.password)

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

        sid: int = -1
        sub = None
        root = rpc[0]
        nsmap = rpc[0].nsmap

        periodic_elm = root.find('yp:periodic', nsmap)
        on_change_elm = root.find('yp:on-change', nsmap)
        datastore_elm = root.find('yp:datastore', nsmap)
        datastore_xpath_filter_elm = root.find(
            'yp:datastore-xpath-filter', nsmap)

        if periodic_elm is not None:
            period_elm = periodic_elm.find('yp:period', nsmap)
            period = int(period_elm.text)
            sub_type = Subscription.PERIODIC

            anchor_time_elm = periodic_elm.find('yp:anchor-time', nsmap)
            anchor_time = None
            if anchor_time_elm is not None:
                anchor_time = anchor_time_elm.text


        elif on_change_elm is not None:
            sub_type = Subscription.ON_CHANGE
        else:
            # Malformed request
            return ncutil.leaf_elm('error', 'Neither periodic nor on change found in establish-subscription request')

        xpath_filter = datastore_xpath_filter_elm.text
        datastore = datastore_elm.text

        if sub_type == Subscription.PERIODIC:
            sid = self.get_next_sub_id()
            sub = Subscription(sid, sub_type, datastore, period=period, datastore_xpath_filter=xpath_filter,
                               raw=etree.tostring(rpc, pretty_print=True).decode('utf8'), anchor_time=anchor_time)
            self.subscriptions[sid] = sub

        # Generate response
        res_map = {
            None: 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'}

        # id tag containing the subscription id
        res = etree.Element('id', nsmap=res_map)
        res.text = str(sid)

        logger.debug(etree.tostring(rpc, pretty_print=True).decode('utf8'))
        logger.debug(etree.tostring(res, pretty_print=True).decode('utf8'))

        if not self.datasource.xpath_exists(sub.datastore_xpath_filter):
            raise ValueError("XPath does not correspond to any data")

        PeriodicNotificationThread(sub, self.datasource, session)

        return res

    def get_next_sub_id(self):
        self.last_subscription_id += 1
        return self.last_subscription_id