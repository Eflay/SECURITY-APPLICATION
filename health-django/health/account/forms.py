from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms


class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    class Meta(UserCreationForm.Meta):

        model = get_user_model()
        fields = ('email', 'first_name', 'last_name',
                  'role', 'protected_symetric_key', 'public_key', 'protected_private_key')
        widgets = {
            'protected_symetric_key': forms.HiddenInput(),
            'protected_private_key': forms.HiddenInput(),
            'public_key': forms.HiddenInput()
        }

        help_text = {
            'password1': None,
            'password2': None
        }

class LoginForm(forms.Form):
    email = forms.CharField(max_length=63, label='E-mail')
    password = forms.CharField(max_length=130, widget=forms.PasswordInput, label='Password')