from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model

from django.forms.utils import ErrorList
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from django.forms import modelformset_factory, HiddenInput, BaseModelFormSet

from django.contrib.auth.forms import PasswordChangeForm
from .models import Post, PostCommunity, PostComment, PostCategory, PostCommentReply, PollChoice, PollVote
from user.models import CustomUser


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["community", "category", "title", "body", "image"]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'body': forms.Textarea(attrs={'placeholder': 'Body'}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Set form-level attributes
        self.helper.form_id = 'id-postForm'
        self.helper.form_class = 'blueForms create-post-form'
        self.helper.form_method = 'post'
        self.helper.form_action = ''  # URL for action, empty means submit to the same URL

        # Configure layout and add classes
        self.helper.layout = Layout(
            Div(
                Field('community', css_class='form-select form-select-lg mb-3'),
                css_class='select-container mb-4'
            ),
            Field('title', css_class='form-control form-control-lg title'),
            Field('body', css_class='form-control body'),
            Submit('submit', 'Post', css_class='btn btn-outline-dark mt-4')
        )


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['comment_body']
        widgets = {
            'comment_body': forms.Textarea(attrs={
                'class': 'form-control comment-textarea',
                'id': 'CommentFormControlTextarea1',
                'rows': '2',
            })
        }

    def __init__(self, *args, **kwargs):
        super(PostCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # No need to redefine css_class here since it's already in the widget
            Field('comment_body')
        )


class PostCommentReplyForm(forms.ModelForm):
    class Meta:
        model = PostCommentReply
        fields = ['reply_body']
        widgets = {
            'reply_body': forms.Textarea(attrs={
                'class': 'form-control reply-comment-textarea',
                'rows': 2,
                'placeholder': 'Write a reply...',
                'style': 'display: none;',
            }),
        }


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'department']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@ucp.edu.pk',
                'id': 'emailInputField',
                'disabled': True  # Make the email field disabled
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username123',
                'id': 'usernameInputField',
            }),
            'department': forms.Select(attrs={
                'class': 'form-select form-select-sm',
                'id': 'departmentSelectField',
                'aria-label': 'Small select example',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True  # Keep the email field disabled


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control profile-update-password',
            'id': 'inputOldPassword',
            'placeholder': 'Enter old password'
        })
    )

    new_password1 = forms.CharField(
        label="Enter New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control profile-update-password',
            'id': 'inputNewPassword',
            'aria-describedby': 'passwordHelpBlock',
            'placeholder': 'Enter new password'
        }),
        help_text="Your password must be 8-20 characters long, contain letters and numbers, and must not contain spaces, special characters, or emoji."
    )

    new_password2 = forms.CharField(
        label="Re-Enter New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control profile-update-password',
            'id': 'inputConfirmNewPassword',
            'aria-describedby': 'passwordHelpBlock',
            'placeholder': 'Confirm new password'
        })
    )


# class PollChoiceForm(forms.ModelForm):
#     class Meta:
#         model = PollChoice
#         fields = ['choice_text']
#         widgets = {
#             'choice_text': forms.TextInput(attrs={'placeholder': 'Enter choice text'}),
#         }


class PollChoiceForm(forms.ModelForm):
    class Meta:
        model = PollChoice
        fields = ['choice_text']
        widgets = {
            'choice_text': forms.TextInput(attrs={
                'placeholder': 'Enter choice text',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PollChoiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Do not render a <form> tag
        self.helper.layout = Layout(
            Field('choice_text', css_class='mb-0', placeholder='Enter choice text', wrapper_class='mb-0')
        )


class BasePollChoiceFormSet(BaseModelFormSet):
    deletion_widget = HiddenInput


PollChoiceFormSet = modelformset_factory(
    PollChoice,
    form=PollChoiceForm,
    formset=BasePollChoiceFormSet,  # Use the custom formset class
    extra=0,
    min_num=2,
    validate_min=True,
    can_delete=True
)