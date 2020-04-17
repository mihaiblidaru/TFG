from threading import Thread, Lock
import socket
import json

class JsonSimpleIPCServer:
    def __init__(self, rec_msg_callback, port=55554):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(0.2) # timeout for listening
        self.s.bind(('0.0.0.0', port))
        self.s.listen(10)
        self.keep_running = True

        t = Thread(name="JsonSimpleIPCServerThread", daemon=True, target=self.accept_connections)
        t.start()

        if not callable(rec_msg_callback):
            raise TypeError("rec_msg_callback is not callable")

        self.rec_msg_callback = rec_msg_callback

    def accept_connections(self):
        
        while self.keep_running:
            try:
                conn, addr = self.s.accept()
            except socket.timeout:
                pass
            except:
                self.keep_running = False
            else:
                t = Thread(target=self.read_data, daemon=True, args=(conn, addr))
                t.start()

    def read_data(self, conn, addr):
        msg = b''
        while True:
            try:
                data = conn.recv(1024)
            except:
                break
            else:
                if not data:
                    break
                
                end_of_msg = data.find(b'\0')
                if  end_of_msg != -1:
                    msg += data[:end_of_msg]
                    decoded_msg = msg.decode('utf-8')
                    obj = json.loads(decoded_msg)
                    res = self.rec_msg_callback(obj)
                    res_json_bytes = json.dumps(res).encode('utf-8') + b'\0'
                    conn.sendall(res_json_bytes)
                    msg = b''
                else:
                    msg += data

class JsonSimpleIPCClient:

    def __init__(self, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('localhost', port))

    def send_msg_sync(self, msg_obj):
        encoded_msg = json.dumps(msg_obj).encode('utf-8') + b'\0'
        self.s.sendall(encoded_msg)

        msg = b''
        while True:
            try:
                data = self.s.recv(1024)
            except:
                break
            else:
                if not data:
                    break
                
                end_of_msg = data.find(b'\0')
                if  end_of_msg != -1:
                    msg += data[:end_of_msg]
                    decoded_msg = msg.decode('utf-8')
                    obj = json.loads(decoded_msg)
                    return obj
                else:
                    msg += data
    
    def close(self):
        self.s.shutdown(1)
        self.s.close()





