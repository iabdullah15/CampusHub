from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from CampusHub import settings

app_name = "user"


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("sign-up", views.SignUpView.as_view(), name="sign-up"),
    path("sign-in", LoginView.as_view(template_name="sign-in.html", next_page='/home'), name="sign-in"),
    path(
        "logout",
        LogoutView.as_view(next_page='/sign-in'),
        name="logout",
    ),
]
