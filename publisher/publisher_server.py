from netconf import nsmap_update, server
import netconf.util as ncutil
from time import sleep
from netconf import util
import getpass

MODEL_NS = "urn:my-urn:my-model"
nsmap_update({'pfx': MODEL_NS})

class MyServer (object):
    def __init__ (self, user, pw):
        server_ctl = server.SSHUserPassController(username='admin', password="admin")
        nc_server = server.NetconfSSHServer(server_ctl=server_ctl,
                                            server_methods=self,
                                            port=55555,
                                            host_key="ssh/id_rsa",
                                            debug=True)

    def nc_append_capabilities(self, caps):
        ncutil.subelm(caps, "capability").text = MODEL_NS
    
    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):
        return util.elm("nc:ok")

    def rpc_my_cool_rpc (self, session, rpc, *params):
        data = ncutil.elm("data")
        data.append(ncutil.leaf_elm("pfx:result", "RPC result string"))
        return data

# ...
a = MyServer("admin", "admin")




while True:
    sleep(1000)


# ...