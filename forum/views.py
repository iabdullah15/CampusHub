from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest

from .models import PostCommunity, Post
from .forms import PostForm
from django.contrib import messages


class HomePageView(View):

    template_name = "forum/home/home-v2.html"

    def get(self, request: HttpRequest):

        communities = PostCommunity.objects.all().order_by('community_name')
        cs_category = PostCommunity.objects.get(community_name='FOIT and CS')
        cs_posts = Post.objects.filter(category=cs_category)

        return render(request, self.template_name, {'posts': cs_posts, 'communities': communities})


class CreatePostView(View):

    template_name = "forum/post/create-post.html"

    def post(self, request: HttpRequest):

        form = PostForm(request.POST)

        if form.is_valid():

            category = form.cleaned_data.get('category')
            print(category)
            title = form.cleaned_data.get('title')
            body = form.cleaned_data.get('body')
            post_category = PostCommunity.objects.get(community_name=category)
            author = request.user

            post = form.save(commit=False)

            # Set additional fields
            post.category = post_category
            post.author = author

            # Now save the post instance to the database
            post.save()

            # Add a success message:

            messages.success(request, "Post created successfully")

            return redirect("forum:home")

        # If the form is invalid, render the form again with errors (this part is commented out, but you might want it)
        return render(request, self.template_name, {'form': form})

    def get(self, request: HttpRequest):
        form = PostForm()

        return render(request, self.template_name, {'form': form})


class PostDetailView(View):
    
    template_name = 'forum/post/post-detail.html'
    
    def get(self, request:HttpRequest, pk:int):
        
        try:
            
            post = Post.objects.get(id=pk)

            return render(request, self.template_name, {"post":post})
        
        except:
            
            return render(request, self.template_name, {})