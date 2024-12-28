from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PostLikes, PostComment, PostCommentReply
from .utils import (
    create_post_like_notification,
    create_post_comment_notification,
    create_comment_like_notification,
    create_comment_reply_notification,
)

@receiver(post_save, sender=PostLikes)
def notify_post_liked(sender, instance, created, **kwargs):
    if created and instance.is_liked:
        # Notify the post author
        if instance.post.author != instance.user:
            create_post_like_notification(
                sender=instance.user, recipient=instance.post.author, post=instance.post
            )

@receiver(post_save, sender=PostComment)
def notify_post_commented(sender, instance, created, **kwargs):
    if created:
        # Notify the post author
        if instance.post.author != instance.author:
            create_post_comment_notification(
                sender=instance.author,
                recipient=instance.post.author,
                post=instance.post,
                comment=instance,
            )

@receiver(post_save, sender=PostCommentReply)
def notify_comment_replied(sender, instance, created, **kwargs):
    if created:
        # Notify the comment author
        if instance.comment.author != instance.author:
            create_comment_reply_notification(
                sender=instance.author,
                recipient=instance.comment.author,
                comment=instance.comment,
                reply=instance,
            )

@receiver(post_save, sender=PostLikes)
def notify_comment_liked(sender, instance, created, **kwargs):
    # Example for comment likes (assuming you have a CommentLikes model)
    if created and instance.is_liked and hasattr(instance, "comment"):
        if instance.comment.author != instance.user:
            create_comment_like_notification(
                sender=instance.user,
                recipient=instance.comment.author,
                comment=instance.comment,
            )
