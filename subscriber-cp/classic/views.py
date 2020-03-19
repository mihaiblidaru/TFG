import socket

from django.shortcuts import render, redirect
from netconf.client import NetconfSSHSession
from classic.forms import AddSubscriptionForm, AddHost
from data.models import Host, Subscription
import lxml
from netconf import util
from netconf import nsmap_update

MODEL_NS = "urn:my-urn:my-model"

nsmap_update({'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push',
              'ds': 'urn:ietf:params:xml:ns:yang:ietf-datastores'})


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

    es_nsmap = {'yp': 'urn:ietf:params:xml:ns:yang:ietf-yang-push'}
    root = lxml.etree.Element('establish-subscription', nsmap=es_nsmap,
                              attrib={'xmlns': 'urn:ietf:params:xml:ns:yang:ietf-subscribed-notifications'})

    datastore = util.leaf_elm('yp:datastore', 'ds:operational')
    root.append(datastore)

    datastore_xpath_filter = util.leaf_elm('yp:datastore-xpath-filter', data['data'])

    root.append(datastore_xpath_filter)

    periodic = util.subelm(root, 'yp:periodic')
    period = util.leaf_elm("yp:period", 500)
    periodic.append(period)

    rval = session.send_rpc(root)

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
