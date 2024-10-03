from django.db import models
from django.conf import settings


class PostCommunity(models.Model):

    community_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.community_name

    class Meta:

        db_table = "forum_postcommunity"


class PostCategory(models.Model):

    category_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.category_name


class Post(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    body = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(PostCommunity, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
