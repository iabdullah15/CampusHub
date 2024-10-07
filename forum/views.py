from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages


from .models import PostCommunity, Post, PostComment, PostCategory, PostLikes
from .forms import PostForm, PostCommentForm
from .helpers import ask_assistant

class HomePageView(View):

    template_name = "forum/home/home-v2.html"

    def get(self, request: HttpRequest):

        communities = PostCommunity.objects.all().order_by('community_name')
        cs_category = PostCommunity.objects.get(community_name='FOIT and CS')
        cs_posts = Post.objects.filter(community=cs_category)

        return render(request, self.template_name, {'posts': cs_posts, 'communities': communities})


class CreatePostView(View):

    template_name = "forum/post/create-post.html"

    def post(self, request: HttpRequest):

        form = PostForm(request.POST)

        if form.is_valid():

            community = form.cleaned_data.get('community')
            print(community)
            title = form.cleaned_data.get('title')
            body = form.cleaned_data.get('body')
            post_category = PostCommunity.objects.get(community_name=community)
            author = request.user

            post = form.save(commit=False)
            
            # Format data to send to translation bot
            content = f'{title}\n\n{body}'
            ask_assistant(query=content)

            # Set additional fields
            post.community = post_category
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

    def get(self, request: HttpRequest, pk: int):
        
        try:
            post = Post.objects.get(id=pk)
            comments = PostComment.objects.filter(post=post).order_by('-time_created')
            comment_form = PostCommentForm()
            
            comment_count = comments.count()

            # Check if the post is liked by the current user
            is_liked_by_user = post.likes.filter(user=request.user, is_liked=True).exists()
            print(is_liked_by_user)
            return render(request, self.template_name, {
                "post": post, 
                "comment_form": comment_form, 
                "comments": comments,
                "is_liked_by_user": is_liked_by_user,  # Pass to the template
                "comment_count":comment_count,
            })
            
        except Post.DoesNotExist:
            return render(request, self.template_name, {})


class PostCommentView(View):

    def post(self, request: HttpRequest, post_id: int):

        form = PostCommentForm(request.POST)
        
        post = Post.objects.get(id=post_id)

        if form.is_valid():

            comment_body = form.cleaned_data.get('comment_body')
            author = request.user
            
            comment = form.save(commit=False)
            
            # Add other fields 
            comment.author = author
            comment.post = post
            
            # Save comment
            
            comment.save()
            messages.success(request, 'Comment added successfully')
            

            return redirect(reverse_lazy('forum:post_detail', args=[post_id]))
        
        return render(request, 'forum/post/post_detail', {"post":post, "comment_form": form})


class LikePostView(View):
    
    def post(self, request, post_id):
        
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        # Get or create a PostLikes object
        post_like, created = PostLikes.objects.get_or_create(user=user, post=post)

        if not created:
            # Toggle the 'is_liked' field if the like object already exists
            post_like.is_liked = not post_like.is_liked
            post_like.save()

        print(post.likes.filter(is_liked=True).count())
        # Return JSON response to update the frontend
        return JsonResponse({
            'liked': post_like.is_liked,
            'total_likes': post.likes.filter(is_liked=True).count(),
        })