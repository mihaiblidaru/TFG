from threading import Thread, Lock
from time import sleep
from simple_ipc import JsonSimpleIPCServer
from netconf.client import NetconfSSHSession
from copy import deepcopy

class ClientDaemon:

    def __init__(self):
        self.global_read_lock = Lock()
        self.ipc_server = JsonSimpleIPCServer(self.ipc_msg_recived)
        self.sessions = {}
        self.session_sockets = {}


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

    def ipc_msg_recived(self, msg):
        if msg['action'] == 'get-active-sessions':
            return self.get_open_session_list()
        elif msg['action'] == 'open-session':
            return self.open_session(msg["params"])
        


        

        return {"fuck": "fuck"}


def main():
    ClientDaemon()

    while True:
        sleep(100)



    





if __name__ == "__main__":
    main()