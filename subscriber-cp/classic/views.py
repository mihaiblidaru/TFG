from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.shortcuts import render
from data.models import Host
from netconf.client import NetconfSSHSession


def index(request):
    hosts = Host.objects.all()

    _dict = {
        'hosts': hosts
    }
    return render(request, 'list.html', _dict)


def show_host(request, slug):
    host = Host.objects.get(slug=slug)

    is_host_online = True

    NetconfSSHSession(host.ip, username='admin', password="admin", port=host.port, debug=True).close()




    _dict = {
        'host': host,
        'online': is_host_online
    }

    return render(request, 'host.html', _dict)

