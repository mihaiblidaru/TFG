import netconf.util as ncutil
from lxml import etree as ET
from netconf import nsmap_update, server
import threading
import time
from datetime import datetime
import json
import xmljson
import logging

logger = logging.getLogger("publisher")

class Subscription():

    PERIODIC = 'periodic'
    ON_CHANGE = 'on_change'

    def __init__(self, sid, stype, datastore, data, **kwargs):
        self.sid = sid
        self.stype = stype
        self.data = data
        self.datastore = datastore
        self.raw = None

        if stype == Subscription.PERIODIC and 'interval' in kwargs:
            self.interval = kwargs['interval']
        
        if 'raw' in kwargs:
            self.raw = kwargs['raw']

    def to_dict(self):
        _dict = {
            'sid': self.sid,
            'stype': self.stype,
            'datastore': self.datastore,
            'data': self.data,
            'raw': self.raw
        }

        if self.stype == Subscription.PERIODIC:
            _dict['interval'] = self.interval

        return _dict

    def __str__(self):
        return str(self.to_dict())

    @staticmethod
    def from_dict(d):
        sub = Subscription(d['sid'], d['stype'], d['datastore'], d['data'], d['dest'])

        if 'interval' in d:
            sub.interval = d['interval']
        
        if 'raw' in d:
            sub.raw = d['raw']

        return sub

class OnChangeNotificationThread:

    def __init__(self, sub, db, session):
        # Keep the notification thread active
        self.keep_active = True

        thread = threading.Thread(target=self.send_on_change_notification, args=(sub, db, session), name=f"ThreadSub{sub.sid}")
        # 
        thread.setDaemon(True)
        thread.start()
    
    def stop(self):
        self.keep_active = False

    def send_on_change_notification(self, sub, session):
        while self.keep_active:
            # If the session is still open send notification
            if session.session_open:
                print(f"Sending notification for subid {sub.sid}") # TODO use logger instead of prints

                nsmap = {None:'urn:ietf:params:xml:ns:netconf:notification:1.0'}
                root = ET.Element('notification', nsmap=nsmap)

                eventTime = ncutil.subelm(root, "eventTime")
                eventTime.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                ucode = ET.tounicode(root)
                print(ucode)
                session.send_message(ucode)
                time.sleep(sub.interval)
            else:
                self.keep_active = False


class PeriodicNotificationThread:

    def __init__(self, sub, db, session):

        self.keep_active = True

        thread = threading.Thread(target=self.send_periodic_notification, args=(sub, db, session), name=f"ThreadSub{sub.sid}")
        # 
        thread.setDaemon(True)
        thread.start()
        
    def send_periodic_notification(self, sub, db, session):
        logger.debug("New periodic subscription thread started")

        while self.keep_active:
            # If the session is still open send notification
            if session.session_open:
                logger.debug(f"Sending notification for subid {sub.sid}")

                push_update = ncutil.elm("push-update")

                # Set notification id
                ncutil.subelm(push_update, "id").text = str(sub.sid)
                datastore_contents = ncutil.subelm(push_update, "datastore-contents")

                # Vamos a suponer de momento de trabajamos con una sola coleccion y un único documento
                doc = db['data'].find_one()
                
                xml_doc = xmljson.parker.etree(doc, root=ET.Element("root"))
                xpath_real = "/root/" + sub.data
                notif_data = xml_doc.xpath(xpath_real)
                for elem in notif_data:
                    datastore_contents.append(elem)


                # TODO: do not access the low level method directly
                session.send_notification(push_update)
                time.sleep(sub.interval)
            else:
                self.keep_active = False