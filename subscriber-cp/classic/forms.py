from django import forms

from data.models import Host


class AddSubscriptionForm(forms.Form):
    host_id = forms.IntegerField(widget=forms.HiddenInput())
    type = forms.CharField(max_length=128)
    data = forms.CharField(max_length=128)
    interval = forms.IntegerField()


class AddHost(forms.ModelForm):
    name = forms.CharField(max_length=100)
    ip = forms.CharField(max_length=100)
    port = forms.IntegerField(max_value=2 ** 16 - 1)

    class Meta:
        model = Host
        fields = ('name', 'ip', 'port')
