from .models import Notification

def create_post_like_notification(sender, recipient, post):
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        category=Notification.Category.POST_LIKED,
        post=post,
    )

def create_post_comment_notification(sender, recipient, post, comment):
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        category=Notification.Category.POST_COMMENTED,
        post=post,
        comment=comment,
    )

def create_comment_like_notification(sender, recipient, comment):
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        category=Notification.Category.COMMENT_LIKED,
        comment=comment,
    )

def create_comment_reply_notification(sender, recipient, comment, reply):
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        category=Notification.Category.COMMENT_REPLIED,
        comment=comment,
        reply=reply,
    )
