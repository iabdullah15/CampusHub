from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path('posts/search', views.PostSearchView.as_view(), name='post_search'),
    path("<str:username>/profile", views.ProfileView.as_view(), name='profile'),
    path("admin-panel", views.AdminPanel.as_view(), name='admin_panel'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path("new-post", views.CreatePostView.as_view(), name="create_post"),
    path('post/edit/<int:post_id>/', views.EditPostView.as_view(), name='edit_post'),
    path("new-poll", views.CreatePostWithPollView.as_view(), name='create_poll'),
    
    path("vote/<int:post_id>/<int:poll_id>", views.Vote.as_view(), name='poll_vote'),
    path("post/<int:pk>", views.PostDetailView.as_view(), name='post_detail'),
    path("community/<int:community_id>", views.CommunityView.as_view(), name='community_page'),
    path('post/like/<int:post_id>', views.LikePostView.as_view(), name='like-post'),
    path("post/comment/<int:post_id>", views.PostCommentView.as_view(), name='post_comment'),
    path("post/comment/<int:comment_id>/reply", views.PostReplyView.as_view(), name='post_reply'),
    path('comment/<int:comment_id>/like/', views.LikeCommentView.as_view(), name='like_comment'),
    path('delete-post/<int:post_id>', views.DeletePost.as_view(), name='delete_post'),
    path('disregard-post/<int:post_id>', views.DisregardReports.as_view(), name='disregard_reports'),
    path("report-post/<int:post_id>/", views.ReportPost.as_view(), name="report_post"),
    path("reports/<int:post_id>", views.ViewReports.as_view(), name='view_reports'),
    # path('poll/edit/<int:post_id>/', views.UpdatePostWithPollView.as_view(), name='edit_poll'),
    path('poll/edit/<int:post_id>/', views.UpdatePostWithPollView.as_view(), name='edit_poll'),
    path('comments/edit/<int:comment_id>/', views.EditComment.as_view(), name='edit_comment'),

]
