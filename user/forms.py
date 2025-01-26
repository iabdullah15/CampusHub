from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


# class CustomUserCreationForm(UserCreationForm):

#     class Meta:

#         model = CustomUser
#         fields = {
#             "email",
#             "username",
#             "password1",
#             "password2",
#         }

class CustomUserCreationForm(UserCreationForm):
    allowed_email_domain = None 

    class Meta:
        model = CustomUser
        fields = {
            "email",
            "username",
            "password1",
            "password2",
        }

    def __init__(self, *args, **kwargs):
        self.allowed_email_domain = kwargs.pop("allowed_email_domain", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self.allowed_email_domain:
            if not email.endswith(f"@{self.allowed_email_domain}"):
                raise forms.ValidationError(
                    f"Only emails ending with @{self.allowed_email_domain} are allowed."
                )
        return email

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