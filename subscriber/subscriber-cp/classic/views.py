import socket

from django.shortcuts import render, redirect
from classic.forms import AddSubscriptionForm, OpenSessionForm
from simple_ipc import JsonSimpleIPCClientUnix


def open_session(request):
    form = OpenSessionForm()

    if request.method == 'POST':
        form = OpenSessionForm(request.POST)

        if form.is_valid():
            client = JsonSimpleIPCClientUnix("NetconfClientDaemon")
            res = client.send_msg_sync({"action":"open-session", "params":form.cleaned_data})

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


def add_subscription(request, slug):

    if request.method == 'POST':
        form = AddSubscriptionForm(request.POST, initial={'host_id': host.id})
    else:
        return render(request, 'add_sub.html', {'form': form})


def index(request):
    #hosts = Host.objects.all()
    client = JsonSimpleIPCClientUnix("NetconfClientDaemon")
    
    res = client.send_msg_sync({"action": "get-active-sessions"})

    _dict = {
        'hosts': res
    }
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
