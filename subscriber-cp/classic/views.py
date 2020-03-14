import socket

from django.shortcuts import render, redirect
from netconf.client import NetconfSSHSession
from classic.forms import AddSubscriptionForm, AddHost
from data.models import Host, Subscription


def add_host(request):
    form = AddHost()

    if request.method == 'POST':
        form = AddHost(request.POST)

        if form.is_valid():
            form.save()

            return render(request, 'add_host.html', {'success': True, 'form': form})
        return render(request, 'add_host.html', {'success': False, 'form': form})

    else:
        return render(request, 'add_host.html', {'form': form})


def del_subscription(resquest, slug, sub_id):
    Host.objects.get(slug=slug).subscription_set.get(id=sub_id).delete()
    return redirect('show_host', slug)


def try_establish_subscription(host, data):
    session = NetconfSSHSession(host.ip, username="admin", password="admin", port=host.port, debug=True)
    query = f"""
        <establish-subscription
        xmlns="urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications"
        xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push">
        <yp:datastore
            xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">
        ds:operational
        </yp:datastore>
        <yp:datastore-xpath-filter
            xmlns:ex="https://example.com/sample-data/1.0">
        {data['data']}
        </yp:datastore-xpath-filter>
        <yp:periodic>
        <yp:period>{data['interval']}</yp:period>
        </yp:periodic>
        </establish-subscription>
    """
    rval = session.send_rpc(query)

    session.close()


def add_subscription(request, slug):
    host = Host.objects.get(slug=slug)
    form = AddSubscriptionForm(initial={'type': 'periodic', 'data': 'cpu.temp', 'host_id': host.id})

    if request.method == 'POST':
        form = AddSubscriptionForm(request.POST, initial={'host_id': host.id})

        if form.is_valid():
            try_establish_subscription(host, form.cleaned_data)

            sub = Subscription(**form.cleaned_data)

            sub.save()

            return render(request, 'add_sub.html', {'success': True, 'form': form})
    else:
        return render(request, 'add_sub.html', {'form': form})


def index(request):
    hosts = Host.objects.all()

    _dict = {
        'hosts': hosts
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
