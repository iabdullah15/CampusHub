from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from CampusHub import settings
from django.views.generic import TemplateView

app_name = "user"


urlpatterns = [
    # path("", views.HomePageView.as_view(), name="home"),
    path("sign-up", views.SignUpView.as_view(), name="sign-up"),
    path("sign-in", LoginView.as_view(template_name="sign-in.html",
         next_page=reverse_lazy('forum:home')), name="sign-in"),
    path(
        "logout",
        LogoutView.as_view(next_page=reverse_lazy('user:sign-in')),
        name="logout",
    ),
    path("verification-sent", views.VerificationSentView.as_view(),
         name="verification-sent"),
    path('password/reset', views.ForgotPasswordView.as_view(), name='password_reset'),
    path('password/reset-done', TemplateView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('password/reset-email-sent', TemplateView.as_view(template_name='password/email_sent.html'), name='email-sent')

]
