from django import forms
from django.utils import timezone

class AuctionForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    description = forms.CharField(widget=forms.Textarea)
    start_price = forms.FloatField(label='Starting Price')
    category = forms.CharField(required=False)
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))