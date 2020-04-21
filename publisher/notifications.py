import netconf.util as ncutil
from lxml import etree as ET
from netconf import nsmap_update, server
import threading
import time
from datetime import datetime
import json
import xmljson
import logging
import traceback

logger = logging.getLogger("publisher")


def every(delay, task):
  next_time = time.time() + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    try:
      task()
    except Exception:
      traceback.print_exc()
      # in production code you might want to have this instead of course:
      # logger.exception("Problem while executing repetitive task.")
    # skip tasks if we are behind schedule:
    next_time += (time.time() - next_time) // delay * delay + delay

class Subscription():

    PERIODIC = 'periodic'
    ON_CHANGE = 'on_change'

    def __init__(self, session_id, subscription_type, datastore, **kwargs):
        self.session_id = session_id
        self.subscription_type = subscription_type
        
        self.datastore_subtree_filter = kwargs.get('datastore_xpath_filter', None)
        self.datastore_xpath_filter = kwargs.get('datastore_xpath_filter', None)

        self.anchor_time = kwargs.get("anchor_time", None)
        self.dampening_period = kwargs.get("dampening_period", None)

        self.datastore = datastore
        self.raw = None

        if subscription_type == Subscription.PERIODIC:
            self.period = kwargs['period']
            self.period_seconds = self.period / 100.0
        
        if 'raw' in kwargs:
            self.raw = kwargs['raw']


class OnChangeNotificationThread:

    def __init__(self, sub, db, session):
        # Keep the notification thread active
        self.keep_active = True

        thread = threading.Thread(target=self.send_on_change_notification, args=(sub, db, session), name=f"ThreadSub{sub.session_id}")
        # 
        thread.setDaemon(True)
        thread.start()
    
    def stop(self):
        self.keep_active = False

    def send_on_change_notification(self, sub, session):
        pass


class PeriodicNotificationThread:

    def __init__(self, sub, db, session):

        self.keep_active = True

        thread = threading.Thread(target=self.send_periodic_notification, args=(sub, db, session), name=f"PeriodicNotificationThread{sub.session_id}")
        # 
        thread.setDaemon(True)
        thread.start()
    
    def send_notification(self, session, sub, db):
        logger.debug(f"Sending notification for subid {sub.session_id}")
        push_update = ncutil.elm("yp:push-update")

        # Set notification id
        ncutil.subelm(push_update, "id").text = str(sub.session_id)
        datastore_contents = ncutil.subelm(push_update, "datastore-contents")

        if sub.datastore_xpath_filter:

            # #Vamos a suponer de momento de trabajamos con una sola coleccion y un único documento
            # doc = db['data'].find_one()
            
            # xml_doc = xmljson.parker.etree(doc, root=ET.Element("root"))
            # xpath_real = "/root/" + sub.datastore_xpath_filter
            # notif_data = xml_doc.xpath(xpath_real)
            # for elem in notif_data:
            #     datastore_contents.append(elem)

            datastore_contents.append(ncutil.leaf_elm("test", 123456789))

        print(ET.tounicode(push_update, pretty_print=True))

        # # TODO: do not access the low level method directly
        session.send_notification(push_update)


    def send_periodic_notification(self, sub, db, session):
        logger.debug("New periodic subscription thread started")
        delay = sub.period_seconds

        next_time = time.time() + delay
        while self.keep_active:
            # If the session is still open send notification
            if session.session_open:
                time.sleep(max(0, next_time - time.time()))
                try:
                    self.send_notification(session, sub, db)
                except Exception:
                    traceback.print_exc()
                
                next_time += (time.time() - next_time) // delay * delay + delay
            else:
                self.keep_active = False

