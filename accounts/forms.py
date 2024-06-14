from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser


class UserRegistrationForm(forms.Form):
    username = forms.CharField(label='Full Name', max_length=100, min_length=5,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Phone Number', max_length=14, min_length=11,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Phone Number',
                                max_length=14, min_length=11,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))


class ProfileForm(forms.ModelForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'phone_number', 'email', 'profile_picture')


class UserContactForm(forms.Form):
    email = forms.EmailField(required=False, label="Email Address")
    phone_number = forms.CharField(max_length=14, required=False, label="Phone Number")
    contact_method = forms.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS')],
        widget=forms.RadioSelect,
        label="Contact Method"
    )
