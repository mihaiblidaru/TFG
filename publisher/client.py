from netconf.client import NetconfSSHSession

host = '127.0.0.1'
port = 55555
username = 'admin'
password = 'admin'

session = NetconfSSHSession("127.0.0.1", username=username, password="admin", port=55555, debug=True)
query = "<get-config xmlns='urn:ietf:params:xml:ns:netconf:base:1.0'><source><running/></source></get-config>"
rval = session.send_rpc(query)


print(rval)

session.close()