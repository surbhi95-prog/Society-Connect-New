from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("full_name", "phone", "wing", "flat_no", "address","society")
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'wing': forms.TextInput(attrs={'placeholder': 'Wing / Building'}),
            'flat_no': forms.TextInput(attrs={'placeholder': 'Flat Number'}),
            'address': forms.Textarea(attrs={
                'placeholder': 'Complete Address',
                'rows': 3
            }),
        }


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('society',)
