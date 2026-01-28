from email.policy import default

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "012 345 678"
        })
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phoneNumber = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', ]


class UploadPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["payment_screenshot"]
        widgets = {
            "payment_screenshot": forms.ClearableFileInput(attrs={"accept": "image/*"})
        }
