from threading import Thread, Lock
from time import sleep
from simple_ipc import JsonSimpleIPCServer
from netconf.client import NetconfSSHSession
from copy import deepcopy
from netconf import nsmap_update
from notification_handler import PrintNotificationHandler, NotificationHandler, MongoNotificationHandler
from lxml import etree
import traceback
from typing import Dict

class ClientDaemon:

    def __init__(self):
        self.global_read_lock = Lock()
        self.ipc_server = JsonSimpleIPCServer(self.ipc_msg_recived, socket_type='unix', unix_socket_filename="NetconfClientDaemon")
        self.sessions = {}
        self.session_sockets : Dict[int, NetconfSSHSession] = {}

        self.handlers = [PrintNotificationHandler(), PrintNotificationHandler()]

        nsmap_update({'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push',
              'ds': 'urn:ietf:params:xml:ns:yang:ietf-datastores',
              'sn': 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'})

    def receive_notifications(self, session: NetconfSSHSession, subscription_id: int):
        while True:
            try:
                notif = session.get_notification(subscription_id)
                for handler in self.handlers:
                    handler(notif, subscription_id, "/")
            except:
                traceback.print_exc()
                break

    def get_open_session_list(self):
        return list(self.sessions.values())
    
    def get_full_client_info(self):
        return list(self.sessions.values())
    
    def close_session(self, params):
        session_id = params['session_id']
        self.session_sockets[session_id].close()
        del self.session_sockets[session_id]
        del self.sessions[session_id]

        return {"status": "ok"}

    def open_session(self, params):
        next_session_id = max(self.session_sockets.keys()) + 1 if self.session_sockets else 1

        res = {"status": None}
        try:
            sess = NetconfSSHSession(params['host'], params['port'], params['username'], params['password'])
            self.session_sockets[next_session_id] = sess
            self.sessions[next_session_id] = {
                "session_id" : next_session_id,
                "host": params['host'],
                "port": params['port'],
                "subscriptions": []
            }

            res["status"] = "ok"
            res["session_id"] = next_session_id
        except Exception as e:
            res["status"] = "error"
            res["msg"] = str(e)
        return res

    def establish_subscription(self, params):
        session_id = params['session_id']
        datastore = params['datastore']
        datastore_xpath_filter = params.get('datastore-xpath-filter', None)
        datastore_subtree_filter = params.get('datastore-subtree-filter', None)
        periodic = params.get('periodic', None)
        on_change = params.get('on-change', None)
        if periodic:
            period = periodic.get('period')
            anchor_time = periodic.get('anchor-time', None)
        elif on_change:
            dampening_period = on_change.get('dampening-period')
            sync_on_start = on_change.get('sync-on-start')
        
        sess = self.session_sockets[session_id]
        try:
            if periodic:
                subscription_id = sess.send_yp_establish_subscription('periodic', datastore, period=period, \
                    anchor_time=anchor_time, datastore_xpath_filter=datastore_xpath_filter, datastore_subtree_filter=datastore_subtree_filter)
            else:
                subscription_id = sess.send_yp_establish_subscription('on-change', datastore, dampening_period=dampening_period, \
                    sync_on_start=sync_on_start, datastore_xpath_filter=datastore_xpath_filter, datastore_subtree_filter=datastore_subtree_filter)
        except Exception as e:
            return {"status":"error", "msg": str(e)}
        else:
            self.sessions[session_id]['subscriptions'].append(subscription_id)
            
            Thread(target=self.receive_notifications, args=(sess, subscription_id), 
                    name=f"ReceiveSubscriptions{subscription_id}", daemon=True).start()
            return {"status":"ok", "subscription_id": subscription_id}

    def ipc_msg_recived(self, msg):
        if msg['action'] == 'get-active-sessions':
            return self.get_open_session_list()
        elif msg['action'] == 'open-session':
            return self.open_session(msg["params"])
        elif msg['action'] == 'close-session':
            return self.close_session(msg["params"])
        elif msg['action'] == 'establish-subscription':
            return self.establish_subscription(msg["params"])
        elif msg['action'] == 'get-full-client-info':
            return self.get_full_client_info()
        
        return {"status": "error", "msg": "Unknown action"}


def main():
    ClientDaemon()

    while True:
        sleep(100)





if __name__ == "__main__":
    main()