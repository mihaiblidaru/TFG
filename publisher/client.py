from netconf.client import NetconfSSHSession


def main():
    host = '127.0.0.1'
    port = 55555
    username = 'admin'
    password = 'admin'

    session = NetconfSSHSession("127.0.0.1", username=username, password="admin", port=55555, debug=True)
    #query = "<get-config xmlns='urn:ietf:params:xml:ns:netconf:base:1.0'><source><running/></source></get-config>"

    query = """
        <establish-subscription
        xmlns="urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications"
        xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push">
        <yp:datastore
            xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">
        ds:operational
        </yp:datastore>
        <yp:datastore-xpath-filter
            xmlns:ex="https://example.com/sample-data/1.0">
        /ex:foo
        </yp:datastore-xpath-filter>
        <yp:periodic>
        <yp:period>500</yp:period>
        </yp:periodic>
        </establish-subscription>
    """
    rval = session.send_rpc(query)


    print(rval)

    session.close()



if __name__ == "__main__":
    main()