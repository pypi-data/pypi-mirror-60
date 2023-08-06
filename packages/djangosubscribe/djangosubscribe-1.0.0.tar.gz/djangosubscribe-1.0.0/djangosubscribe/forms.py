from django import forms
from djangosubscribe.models import SubscriberModel


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = SubscriberModel
        fields = ["email"]

        widgets = {
            "email": forms.EmailInput(attrs={'type': 'text', 'class': 'form-control rounded-0', 'placeholder': 'Email Address.'})
        }
