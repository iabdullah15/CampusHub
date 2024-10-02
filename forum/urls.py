from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("new-post", views.CreatePostView.as_view(), name="create_post")
]
