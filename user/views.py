from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest

from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm

from django_email_verification import send_email


class SignUpView(View):
    def post(self, request: HttpRequest):
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is inactive until email verification
            user.save()

            send_email(user)  # Send verification email

            return redirect(reverse_lazy('user:verification-sent'))

        return render(request, "sign-up.html", {"form": form})

    def get(self, request: HttpRequest):
        return render(request, "sign-up.html", {"form": CustomUserCreationForm()})


class VerificationSentView(TemplateView):
    template_name = "verification-sent.html"


class HomePageView(View):

    template_name = "home.html"

    def get(self, request: HttpRequest):

        return render(request, self.template_name, {})
