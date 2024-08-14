from django.forms import BaseModelForm
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest

from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm

# Create your views here.


class SignUpView(View):

    def post(self, request:HttpRequest):

        form = CustomUserCreationForm(request.POST)

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(f"Password 1: {password1}")
        print(f"Password 2: {password2}")

        if form.is_valid():

            form.save()

            email = form.cleaned_data.get(('email'))
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)

            login(request, user)

            return redirect(reverse_lazy('user:home'))
        
        return render(request, 'sign-up.html', {'form': form})

    
    def get(self, request:HttpRequest):

        return render(request, 'sign-up.html', {'form':CustomUserCreationForm()})






class HomePageView(View):

    template_name = "home.html"

    def get(self, request: HttpRequest):

        return render(request, self.template_name, {})
