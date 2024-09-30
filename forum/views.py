from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest

# Create your views here.


class HomePageView(View):

    template_name = "home/home.html"

    def get(self, request: HttpRequest):

        return render(request, self.template_name, {})