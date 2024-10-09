from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model

from django.forms.utils import ErrorList
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML


from .models import Post, PostCommunity, PostComment, PostCategory, PostCommentReply


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["community", "category", "title", "body"]
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
            Field('comment_body')  # No need to redefine css_class here since it's already in the widget
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