from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest

from .models import PostCategory, Post
from .forms import PostForm
# Create your views here.


class HomePageView(View):

    template_name = "forum/home/home-v2.html"

    def get(self, request: HttpRequest):
        
        cs_category = PostCategory.objects.get(category_name='FOIT and CS')
        cs_posts = Post.objects.filter(category = cs_category)
        
        return render(request, self.template_name, {'posts':cs_posts})
    
    
    
class CreatePostView(View):
    
    template_name = "forum/post/create-post.html"

    
    def post(self, request: HttpRequest):
        
        form = PostForm(request.POST)
        
        if form.is_valid():
            
            category= form.cleaned_data.get('category')
            print(category)
            title = form.cleaned_data.get('title')
            body = form.cleaned_data.get('body')
            post_category = PostCategory.objects.get(category_name=category)
            author = request.user
            
            post = form.save(commit=False)
            # Set additional fields
            post.category = post_category
            post.author = author
            
            # Now save the post instance to the database
            post.save()
            
            # form.save()
            return redirect("forum:home")
        
        # If the form is invalid, render the form again with errors (this part is commented out, but you might want it)
        return render(request, self.template_name, {'form': form})
    
    
    def get(self, request: HttpRequest):
        form = PostForm()
        
        return render(request, self.template_name, {'form': form})
