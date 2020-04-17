from django import forms



class AddSubscriptionForm(forms.Form):
    host_id = forms.IntegerField(widget=forms.HiddenInput())
    type = forms.CharField(max_length=128)
    data = forms.CharField(max_length=128)
    interval = forms.IntegerField()


class OpenSessionForm(forms.Form):
    host = forms.CharField(max_length=100)
    port = forms.IntegerField(max_value=2 ** 16 - 1)

