from django import forms


CATEGORIES = [
    ('art', 'Art'),
    ('electronics', 'Electronics'),
    ('collectibles', 'Collectibles'),
    ('fashion', 'Fashion'),
    ('other', 'Other'),
]

class AuctionForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea)
    start_price = forms.FloatField()
    category = forms.ChoiceField(choices=CATEGORIES, required=False)
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    images = forms.FileField(required=False)