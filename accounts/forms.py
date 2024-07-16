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
