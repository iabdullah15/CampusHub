from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model

from django.forms.utils import ErrorList
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from .models import Post, PostCommunity, PostComment, PostCategory


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "body", "community"]


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