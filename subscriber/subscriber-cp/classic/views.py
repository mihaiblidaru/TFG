import socket

from django.shortcuts import render, redirect
from classic.forms import AddSubscriptionForm, OpenSessionForm
from simple_ipc import JsonSimpleIPCClientUnix
from data.models import KnownHost

def close_session(request, session_id):
    client = JsonSimpleIPCClientUnix("NetconfClientDaemon")
    client.send_msg_sync({"action":"close-session", "params":{"session_id": session_id}})
    return redirect('index')

def delete_known_host(request, known_host_id):
    KnownHost.objects.get(id=known_host_id).delete()
    return redirect('index')

def open_session(request, known_host_id=None):
    initial = None
    if known_host_id:
        known_host = KnownHost.objects.get(id=known_host_id)
        initial = {
            'host': known_host.host,
            'port': known_host.port,
            'username': known_host.username,
            'password': known_host.password
        }
        

    form = OpenSessionForm(initial=initial)

    if request.method == 'POST':
        form = OpenSessionForm(request.POST)

        if form.is_valid():
            client = JsonSimpleIPCClientUnix("NetconfClientDaemon")
            res = client.send_msg_sync({"action":"open-session", "params":form.cleaned_data})

            try:
                KnownHost(**form.cleaned_data).save()
            except:
                pass

            if res["status"] == "ok":
                return render(request, 'open_session.html', {'success': True, 'form': form})
            else:
                return render(request, 'open_session.html', {'success': False, 'form': form, 'error':res["msg"]})
        return render(request, 'open_session.html', {'success': False, 'form': form})

    else:
        return render(request, 'open_session.html', {'form': form})


def del_subscription(resquest, slug, sub_id):
    #Host.objects.get(slug=slug).subscription_set.get(id=sub_id).delete()
    return redirect('show_host', slug)


def add_subscription(request, session_id):
    if request.method == 'POST':
        cli_request = {}
        cli_request['session_id'] = session_id
        cli_request["datastore"] = request.POST['datastore']
        selection_filter = request.POST['selection-filter']

        if selection_filter == 'subtree':
            cli_request["datastore-subtree-filter"] = request.POST["datastore-subtree-filter"]
        else:
            cli_request["datastore-xpath-filter"] = request.POST["datastore-xpath-filter"]

        update_trigger = request.POST['update-trigger']

        if update_trigger == 'periodic':
            periodic = {}
            periodic['period'] = int(request.POST['period'])
            anchor_time = request.POST['anchor-time']
            if len(anchor_time) > 0:
                periodic['anchor-time'] = anchor_time
            cli_request['periodic'] = periodic
        else:
            on_change = {}
            dampening_period = request.POST['dampening-period']
            if dampening_period:
                on_change['dampening-period'] == dampening_period
                    
            sync_on_start = request.POST['sync-on-start']

            if sync_on_start:
                on_change['sync-on-start'] = sync_on_start
        
            cli_request['on_change'] = on_change

        client = JsonSimpleIPCClientUnix("NetconfClientDaemon")
        res = client.send_msg_sync({"action": "establish-subscription", "params":cli_request})
        if res["status"] == "ok":
            return render(request, 'add_sub.html', {'success': True, 'subscription_id': res['subscription_id']})
        else:
            return render(request, 'add_sub.html', {'success': False, 'error':res["msg"]})

    else:
        return render(request, 'add_sub.html')


def index(request):
    try:
        client = JsonSimpleIPCClientUnix("NetconfClientDaemon")
    except:
        return render(request, 'list.html', {"error": "Could not connect to netconf client daemon. Check if active and reload."})
    res = client.send_msg_sync({"action": "get-full-client-info"})

    _dict = {'sessions': res, 'known_hosts': KnownHost.objects.all()}

    return render(request, 'list.html', _dict)
    

def show_host(request, slug):
    host = Host.objects.get(slug=slug)

    # Check if host is online by opening a TCP connection to the given ip and port
    is_host_online = True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host.ip, host.port))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
    except Exception:
        is_host_online = False

    _dict = {
        'host': host,
        'online': is_host_online
    }

    return render(request, 'host.html', _dict)
