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
    community = models.ForeignKey(PostCommunity, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title


class PostComment(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_body = models.CharField(max_length=300)
    time_created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')

    # related name
    # Creates a backwards link
    # I can fetch all comments someone posted using the following:
    # abdullah = PostComment.objects.get(author=author_obj)
    # abdullah.comments.all()

    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.post.title}"
