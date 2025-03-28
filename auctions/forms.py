from django import forms

class AuctionForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea)
    start_price = forms.FloatField()
    category = forms.CharField(required=False)
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    images = forms.FileField(required=False)