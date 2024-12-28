from django.db import models
from django.conf import settings


class PostCommunity(models.Model):

    community_name = models.CharField(max_length=50)
    community_sidebar_logo = models.ImageField(null=True, blank=True)
    community_cover_image = models.ImageField(null=True, blank=True)
    community_post_image = models.ImageField(null=True, blank=True)
    community_description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.community_name

    class Meta:

        db_table = "forum_postcommunity"


class PostCategory(models.Model):

    category_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.category_name   


class PostLikes(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='likes', on_delete=models.CASCADE,
                             blank=True, null=True)  # Add ForeignKey to Post
    is_liked = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f'{self.user.username} liked {self.post.title}'

    class Meta:
        # Ensure a user can only like a post once
        unique_together = ('user', 'post')


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    body = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True)
    community = models.ForeignKey(PostCommunity, on_delete=models.CASCADE)
    category = models.ForeignKey(
        PostCategory, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.title

    @property
    def total_likes(self):
        # Now using the related name to count likes
        return self.likes.filter(is_liked=True).count()


class CommentLike(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    comment = models.ForeignKey('PostComment', related_name='comment_likes',
                                on_delete=models.CASCADE, blank=True, null=True)  # Add ForeignKey to Post
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

    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.post.title}"


class PostCommentReply(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply_body = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(
        PostComment, on_delete=models.CASCADE, related_name='comment_reply')

    def __str__(self) -> str:
        return f"Reply by {self.author.username} on {self.comment}"


class Poll(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name='poll', null=True, blank=True)

    def __str__(self):
        return self.post.title


class PollChoice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return f'{self.choice_text} Choice Name on post with TITLE {self.poll.post.title}'


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(PollChoice, on_delete=models.CASCADE, related_name='vote')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    # Use auto_now to update timestamp on each save
    time_voted = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('poll', 'user')

    def __str__(self):
        return f"{self.user.username} Choice Name on post with TITLE {self.poll.post.title}"
    
    
class Report(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name="reports"
    )
    reason = models.CharField(max_length=50, default='Inappropriate Content')
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'post')  # Ensure one report per user per post

    def __str__(self):
        return f"{self.user.username} reported {self.post.title}"
    
    
    
from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Notification(models.Model):
    
    def get_notification_content(self):
        if self.category == self.Category.POST_LIKED:
            return f"{self.sender.username} liked your post: {self.post.title}"
        elif self.category == self.Category.POST_COMMENTED:
            return f"{self.sender.username} commented on your post: {self.post.title}"
        elif self.category == self.Category.COMMENT_LIKED:
            return f"{self.sender.username} liked your comment: {self.comment.comment_body}"
        elif self.category == self.Category.COMMENT_REPLIED:
            return f"{self.sender.username} replied to your comment: {self.comment.comment_body}"
        return "You have a new notification"
    
    class Category(models.TextChoices):
        POST_LIKED = "post_liked", "Post Liked"
        POST_COMMENTED = "post_commented", "Post Commented"
        COMMENT_LIKED = "comment_liked", "Comment Liked"
        COMMENT_REPLIED = "comment_replied", "Comment Replied"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    post = models.ForeignKey('forum.Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(
        'forum.PostComment', on_delete=models.CASCADE, null=True, blank=True
    )
    reply = models.ForeignKey(
        'forum.PostCommentReply', on_delete=models.CASCADE, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.get_category_display()}"

    class Meta:
        ordering = ['-timestamp']
