from django import forms
from .models import User

class UserRegistForm(forms.ModelForm):
    re_password = forms.PasswordInput()
    class Meta:
        model = User
        # fields = ['user_name', 'password', 'fb_link', 'gender', 'age', 'address']
        fields = ['user_name', 'email', 'password']


class UserLoginForm(forms.ModelForm):
    # user_name = forms.CharField(min_length=1, max_length=100)
    # password = forms.PasswordInput()

    class Meta:
        model = User
        fields = ['user_name', 'password']