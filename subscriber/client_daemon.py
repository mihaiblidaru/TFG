from threading import Thread, Lock
from time import sleep
from simple_ipc import JsonSimpleIPCServer
from netconf.client import NetconfSSHSession
from copy import deepcopy
from netconf import nsmap_update
from lxml import etree
import traceback

class ClientDaemon:

    def __init__(self):
        self.global_read_lock = Lock()
        self.ipc_server = JsonSimpleIPCServer(self.ipc_msg_recived, socket_type='unix', unix_socket_filename="NetconfClientDaemon")
        self.sessions = {}
        self.session_sockets = {}
        nsmap_update({'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push',
              'ds': 'urn:ietf:params:xml:ns:yang:ietf-datastores',
              'sn': 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'})

    def receive_notifications(self, session, subscription_id):
        while True:
            try:
                notif, aaaa = session.get_notification(subscription_id)
                print(etree.tounicode(notif, pretty_print=True), end="\n\n")
            except Exception as e:
                traceback.print_exc()
                break

    def get_open_session_list(self):
        return list(self.sessions.values())

    def open_session(self, params):
        next_session_id = max(self.session_sockets.keys()) + 1 if self.session_sockets else 1

        res = {"status": None}
        try:
            sess = NetconfSSHSession(params['host'], params['port'], 'admin', 'admin')
            self.session_sockets[next_session_id] = sess
            self.sessions[next_session_id] = {
                "session_id" : next_session_id,
                "host": params['host'],
                "port": params['port'],
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
            anchor_time = periodic.get('anchor_time', None)
        elif on_change:
            dampening_period = on_change.get('dampening_period')
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
        finally:
            Thread(target=self.receive_notifications, args=(sess, subscription_id), 
                    name=f"ReceiveSubscriptions{subscription_id}", daemon=True).start()
            return {"status":"ok", "subscription_id": subscription_id}

    def ipc_msg_recived(self, msg):
        if msg['action'] == 'get-active-sessions':
            return self.get_open_session_list()
        elif msg['action'] == 'open-session':
            return self.open_session(msg["params"])
        elif msg['action'] == 'establish-subscription':
            return self.establish_subscription(msg["params"])
        
        return {"status": "error", "msg": "Unknown action"}


def main():
    ClientDaemon()

    while True:
        sleep(100)



    





if __name__ == "__main__":
    main()