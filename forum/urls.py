from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("<str:username>/profile", views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path("new-post", views.CreatePostView.as_view(), name="create_post"),
    path("post/<int:pk>", views.PostDetailView.as_view(), name='post_detail'),
    path("community/<int:community_id>", views.CommunityView.as_view(), name='community_page'),
    path('post/like/<int:post_id>', views.LikePostView.as_view(), name='like-post'),
    path("post/comment/<int:post_id>", views.PostCommentView.as_view(), name='post_comment'),
    path("post/comment/<int:comment_id>/reply", views.PostReplyView.as_view(), name='post_reply'),
    path('comment/<int:comment_id>/like/', views.LikeCommentView.as_view(), name='like_comment'),

]
