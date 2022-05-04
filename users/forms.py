from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.core import validators


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'hi',
        }
    ))

class ContactForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(widget=forms.Textarea)
    honeypot = forms.CharField(widget=forms.HiddenInput, required=False, validators=[validators.MaxLengthValidator(0)])

    # def clean_honeypot(self):
    # 	honeypot = self.cleaned_data['honeypot']
    # 	if len(honeypot):
    # 		raise forms.ValidationError('ngga boleh diisi dong')
    # 	return honeypot
