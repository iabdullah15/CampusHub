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

from django_email_verification import send_email, send_password
from django.contrib.auth import get_user_model

User = get_user_model()


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
    
    
class PasswordResetView(View):
    template_name = 'password/email_form.html'  # The form template

    def get(self, request: HttpRequest):
        # Render the password reset form (GET request)
        return render(request, self.template_name)

    def post(self, request: HttpRequest):
        # Handle form submission (POST request)
        email = request.POST.get('email')
        try:
            # Try to find the user by email
            user = User.objects.get(email=email)
            send_password(user)  # Send password recovery email
            return redirect(reverse_lazy('user:email-sent'))  # Redirect to a success page
        except User.DoesNotExist:
            # If the user does not exist, show an error message on the form
            return render(request, self.template_name, {'error': 'User with this email does not exist'})


class VerificationSentView(TemplateView):
    template_name = "verification-sent.html"


class HomePageView(View):

    template_name = "home.html"

    def get(self, request: HttpRequest):

        return render(request, self.template_name, {})
