from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):

    class Meta:

        model = CustomUser
        fields = {
            "email",
            "username",
            "password1",
            "password2",
        }


class CustomUserChangeForm(UserChangeForm):

    class Meta:

        model = CustomUser
        fields = "__all__"


class UserOnboardingForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        # fields = ['username', 'department']
        fields = ['department']
        
    # username = forms.CharField(
    #     label="Username",
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Enter your username',
    #         'id': 'username'
    #     })
    # )
    
    department = forms.ChoiceField(
        choices=[
            ('Law', 'Law'),
            ('Management Sciences', 'Management Sciences'),
            ('Science and Technology', 'Science and Technology'),
            ('Humanities and Social Sciences', 'Humanities and Social Sciences'),
            ('Media and Mass Communication', 'Media and Mass Communication'),
            ('Engineering', 'Engineering'),
            ('Languages and Literature', 'Languages and Literature'),
            ('Pharmaceutical Sciences', 'Pharmaceutical Sciences'),
            ('FOIT and CS', 'FOIT and CS')
        ],
        widget=forms.Select(attrs={'class': 'form-select department-select'}),
        label="Department"
    )