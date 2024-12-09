from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    # Custom email validation
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class VerificationForm(forms.Form):
    purpose_choices = [
        ("bank", "Bank Work"),
        ("government", "Government Work"),
    ]
    purpose = forms.ChoiceField(choices=purpose_choices, required=True)
    image = forms.ImageField(required=True)




# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=150)
#     password = forms.CharField(widget=forms.PasswordInput)

# class VerificationForm(forms.Form):
#     purpose = forms.ChoiceField(choices=[('Bank Work', 'Bank Work'), ('Government Work', 'Government Work')])
#     image = forms.ImageField()


# class RegistrationForm(forms.Form):
#     username = forms.CharField(max_length=150, required=True)
#     email = forms.EmailField(required=True)
#     password = forms.CharField(widget=forms.PasswordInput, required=True)