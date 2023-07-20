from django import forms


class UserRegistrationForm(forms.Form):
    username = forms.CharField(label='Full Name', max_length=100, min_length=5,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Phone Number', max_length=14, min_length=11,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Phone Number',
                                max_length=14, min_length=11,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
