from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    email = forms.EmailField()
