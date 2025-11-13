from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    email = forms.EmailField()


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
