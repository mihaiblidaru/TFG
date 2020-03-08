from django.contrib import admin
from data.models import Host, Subscription


class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'port')
    exclude = ('slug', )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('host', 'type', 'data')


admin.site.register(Host, HostAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
