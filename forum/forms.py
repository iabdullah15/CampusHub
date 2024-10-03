from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Post, PostCommunity


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "body", "category"]
