from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView


from django.contrib.auth.views import LoginView, LogoutView

from django.http import HttpResponse, HttpRequest
from django.contrib import messages

from .forms import CustomUserChangeForm, CustomUserCreationForm, UserOnboardingForm

from django_email_verification import send_email, send_password
from django.contrib.auth import get_user_model, login
from .models import CustomUser


User = get_user_model()


class SignUpView(View):

    allowed_email_domain = "ucp.edu.pk"  # Define the allowed domain locally

    def post(self, request: HttpRequest):
        # form = CustomUserCreationForm(request.POST)
        form = CustomUserCreationForm(
            request.POST, allowed_email_domain=self.allowed_email_domain
        )


        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is inactive until email verification
            user.save()

            send_email(user)  # Send verification email

            return redirect(reverse_lazy('user:verification-sent'))

        return render(request, "sign-up.html", {"form": form})

    def get(self, request: HttpRequest):
        return render(request, "sign-up.html", {"form": CustomUserCreationForm()})
    
    
class ForgotPasswordView(View):
    template_name = 'password/email_form.html'  # The form template

    def get(self, request: HttpRequest):
        # Render the password reset form (GET request)
        return render(request, self.template_name)

    def post(self, request: HttpRequest):
        # Handle form submission (POST request)
        email = request.POST.get('email')
        try:
            # Try to find the user by email
            user = CustomUser.objects.get(email=email)
            print(email, user)
            send_password(user)  # Send password recovery email
            return redirect(reverse_lazy('user:email-sent'))  # Redirect to a success page
        except User.DoesNotExist:
            # If the user does not exist, show an error message on the form
            return render(request, self.template_name, {'error': 'User with this email does not exist'})


class VerificationSentView(TemplateView):
    template_name = "verification-sent.html"



def onboarding_view(request):
    
    if request.method == 'POST':
        form = UserOnboardingForm(request.POST)
        if form.is_valid():
            print("Hello")
            department = form.cleaned_data.get('department')
            print(department)
            user = request.user
            user.department = department
            user.save()
            return redirect('forum:home')  # Redirect after successful onboarding
    else:
        form = UserOnboardingForm()

    return render(request, 'onboarding.html', {'form': form})



class CustomLoginView(LoginView):
    template_name = "sign-in.html"
    next_page = reverse_lazy('forum:home')

    def form_valid(self, form):
        # Log the user in first
        login(self.request, form.get_user())
        # Add debug logging
        user_department = form.get_user().department
        
        if not user_department:
            return redirect('user:onboarding')  # Redirect to onboarding
        
        # If all checks pass, let the user sign in
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Add debug logging for form errors
        print("Form Invalid Errors:", form.errors)

        # Optionally add error messages for the user
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)