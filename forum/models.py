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


class PostLikes(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='likes', on_delete=models.CASCADE, blank=True, null=True)  # Add ForeignKey to Post
    is_liked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return f'{self.user.username} liked {self.post.title}'
    
    class Meta:
        # Ensure a user can only like a post once
        unique_together = ('user', 'post')
        

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    body = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    community = models.ForeignKey(PostCommunity, on_delete=models.CASCADE)
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.title

    @property
    def total_likes(self):
        # Now using the related name to count likes
        return self.likes.filter(is_liked=True).count()



class CommentLike(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey('PostComment', related_name='comment_likes', on_delete=models.CASCADE, blank=True, null=True)  # Add ForeignKey to Post
    is_liked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_likes(self):
        # Now using the related name to count likes
        return self.likes.filter(is_liked=True).count()
    
    def __str__(self):
        
        return f'{self.user.username} liked {self.comment.comment_body}'
    
    class Meta:
        # Ensure a user can only like a comment once
        unique_together = ('user', 'comment')


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



class PostCommentReply(models.Model):
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply_body = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='comment_reply')
    
    def __str__(self) -> str:
        return f"Reply by {self.author.username} on {self.comment}"