from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(PostCommunity)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(PostLikes)
admin.site.register(PostCategory)
admin.site.register(PostCommentReply)
admin.site.register(Poll)
admin.site.register(PollChoice)
admin.site.register(PollVote)
admin.site.register(Report)