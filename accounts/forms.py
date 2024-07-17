from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email or Phone')


class ProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'profile_picture')


class PhoneLoginForm(forms.Form):
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))

