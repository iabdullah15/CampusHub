from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView

from django.db import transaction
from datetime import timedelta
from django.utils import timezone


from .models import PostCommunity, Post, PostComment, PostCategory, PostLikes, PostCommentReply, CommentLike, Poll, PollChoice, PollVote
from .forms import PostForm, PostCommentForm, PostCommentReplyForm, UpdateProfileForm, CustomPasswordChangeForm, PollChoiceFormSet

from django.contrib.auth import update_session_auth_hash
from .helpers import ask_assistant, moderate_post, determine_moderation_action
from user.models import CustomUser


class HomePageView(View):

    template_name = "forum/home/home-v2.html"

    def get(self, request: HttpRequest):

        communities = PostCommunity.objects.all().order_by('community_name')
        cs_category = PostCommunity.objects.get(community_name='FOIT and CS')
        cs_posts = Post.objects.filter(community=cs_category)

        # Create a list of posts with their like status (Current user)
        posts_with_like_status = []
        for post in cs_posts:
            is_liked_by_user = PostLikes.objects.filter(
                post=post, user=request.user, is_liked=True).exists()
            posts_with_like_status.append({
                'post': post,
                'is_liked_by_user': is_liked_by_user
            })

        print(communities)
        return render(request, self.template_name, {
            'posts_with_like_status': posts_with_like_status,
            'communities': communities,
        })


class CreatePostView(View):

    template_name = "forum/post/create-post.html"

    def post(self, request: HttpRequest):

        form = PostForm(request.POST)

        if form.is_valid():
            community = form.cleaned_data.get('community')
            title = form.cleaned_data.get('title')
            body = form.cleaned_data.get('body')
            post_category = PostCommunity.objects.get(community_name=community)
            author = request.user

            # Check if the user is suspended
            if author.is_suspended and author.suspension_end_date:
                if timezone.now() < author.suspension_end_date:
                    messages.error(
                        request,
                        f"Your account is suspended until {author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}. You cannot create new posts."
                    )
                    return redirect('forum:home')
                else:
                    # Suspension period is over
                    author.is_suspended = False
                    author.suspension_end_date = None
                    author.save()

            # Format content for moderation
            content = f'{title}\n\n{body}'

            
            final_action, actions = moderate_post(post_content=content)

            # Create the post instance but do not save yet
            post = form.save(commit=False)
            post.community = post_category
            post.author = author
            post.moderation_status = final_action
            # post.violation_attributes = attribute_scores if final_action != 'Accept' else None
            post.moderation_timestamp = timezone.now()

            # Handle the final action
            if final_action == 'Accept':
                post.save()
                messages.success(request, "Post created successfully.")
                return redirect('forum:post_detail', pk=post.pk)
            elif final_action == 'Issue Warning':
                # Increment user's warning count
                author.warning_count += 1
                author.save()

                post.save()

                # Inform the user
                warning_attributes = [attr for attr, action in actions.items() if action == 'Issue Warning']
                messages.warning(
                    request,
                    f"Your post has been created but contains content that may violate our guidelines: {', '.join(warning_attributes)}. Please review our community guidelines."
                )
                return redirect('forum:post_detail', pk=post.pk)
            
            elif final_action == 'Reject':
                # Increment user's rejection count
                author.rejection_count += 1
                author.save()
                print(author.rejection_count)

                # Check for suspension
                if author.rejection_count >= 5 and not author.is_suspended:
                    author.is_suspended = True
                    author.suspension_end_date = timezone.now() + timedelta(days=7)
                    author.save()
                    messages.error(
                        request,
                        f"Your post was rejected due to violating our community guidelines. Your account has been suspended until {author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}."
                    )
                else:
                    messages.error(
                        request,
                        "Your post was rejected due to violating our community guidelines. Please review our community guidelines."
                    )
                    
                return render(request, self.template_name, {'form': form})
        else:
            # If the form is invalid, render the form again with errors
            return render(request, self.template_name, {'form': form})

    def get(self, request: HttpRequest):
        form = PostForm()
        return render(request, self.template_name, {'form': form})




class CreatePostWithPollView(View):

    template_name = 'forum/post/create-poll.html'

    def get(self, request: HttpRequest):
        post_form = PostForm()
        poll_choice_formset = PollChoiceFormSet(queryset=PollChoice.objects.none())
        return render(request, self.template_name, {
            'post_form': post_form,
            'poll_choice_formset': poll_choice_formset,
        })

    def post(self, request):
        post_form = PostForm(request.POST)
        poll_choice_formset = PollChoiceFormSet(
            request.POST,
            queryset=PollChoice.objects.none()
        )

        if post_form.is_valid() and poll_choice_formset.is_valid():
            author = request.user

            # Check if the user is suspended
            if author.is_suspended and author.suspension_end_date:
                if timezone.now() < author.suspension_end_date:
                    messages.error(
                        request,
                        f"Your account is suspended until {author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}. You cannot create new posts."
                    )
                    return redirect('forum:home')
                else:
                    # Suspension period is over
                    author.is_suspended = False
                    author.suspension_end_date = None
                    author.save()

            # Extract and validate poll choices
            choices = []
            for form in poll_choice_formset:
                if form.cleaned_data.get('DELETE'):
                    continue  # Skip forms marked for deletion
                choice_text = form.cleaned_data.get('choice_text')
                if choice_text:
                    choices.append(choice_text)

            # Validate minimum number of choices
            if len(choices) < 2:
                messages.error(request, 'Please provide at least two choices for the poll.')
                return render(request, self.template_name, {
                    'post_form': post_form,
                    'poll_choice_formset': poll_choice_formset,
                })

            # Format content for moderation
            title = post_form.cleaned_data.get('title')
            body = post_form.cleaned_data.get('body')
            choices_content = '\n'.join(choices)
            content = f'{title}\n\n{body}\n\nChoices:\n{choices_content}'

            # Perspective API moderation
            final_action, actions = moderate_post(post_content=content)

            # Handle the final action
            if final_action == 'Accept' or final_action == 'Issue Warning':
                with transaction.atomic():
                    # Update user counts if necessary
                    if final_action == 'Issue Warning':
                        author.warning_count += 1
                        author.save()

                    # Save the post
                    post = post_form.save(commit=False)
                    post.author = author
                    post.moderation_status = final_action
                    post.moderation_timestamp = timezone.now()
                    post.save()

                    # Create a poll linked to the post
                    poll = Poll.objects.create(post=post)

                    # Save valid choices
                    for choice_text in choices:
                        PollChoice.objects.create(poll=poll, choice_text=choice_text)

                if final_action == 'Issue Warning':
                    warning_attributes = [attr for attr, action in actions.items() if action == 'Issue Warning']
                    messages.warning(
                        request,
                        f"Your post has been created but contains content that may violate our guidelines: {', '.join(warning_attributes)}. Please review our community guidelines."
                    )
                else:
                    messages.success(request, 'Post with poll created successfully!')

                return redirect('forum:post_detail', pk=post.pk)

            elif final_action == 'Reject':
                # Increment user's rejection count and handle suspension
                with transaction.atomic():
                    author.rejection_count += 1
                    author.save()

                    if author.rejection_count >= 5 and not author.is_suspended:
                        author.is_suspended = True
                        author.suspension_end_date = timezone.now() + timedelta(days=7)
                        author.save()
                        messages.error(
                            request,
                            f"Your post was rejected due to violating our community guidelines. Your account has been suspended until {author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}."
                        )
                    else:
                        messages.error(
                            request,
                            "Your post was rejected due to violating our community guidelines. Please review our community guidelines."
                        )

                # Render the form again without any database operations
                return render(request, self.template_name, {
                    'post_form': post_form,
                    'poll_choice_formset': poll_choice_formset,
                })
        else:
            messages.error(request, 'There was an error in your submission.')

        return render(request, self.template_name, {
            'post_form': post_form,
            'poll_choice_formset': poll_choice_formset,
        })


# class CreatePostWithPollView(View):
    
#     template_name = 'forum/post/create-poll.html'
    
#     def get(self, request:HttpRequest):
        
#         print("Hello")
#         post_form = PostForm()
#         poll_choice_formset = PollChoiceFormSet(queryset=PollChoice.objects.none())
        
#         return render(request, self.template_name, {
#             'post_form': post_form,
#             'poll_choice_formset': poll_choice_formset,
#         })
        
#     def post(self, request):
#         post_form = PostForm(request.POST)
#         poll_choice_formset = PollChoiceFormSet(
#             request.POST,
#             queryset=PollChoice.objects.none()
#         )

#         if post_form.is_valid() and poll_choice_formset.is_valid():
#             with transaction.atomic():
#                 # Save the post
#                 post = post_form.save(commit=False)
#                 post.author = request.user
#                 post.save()

#                 # Create a poll linked to the post
#                 poll = Poll.objects.create(post=post)

#                 # Prepare choices to save
#                 valid_choices = []
#                 for form in poll_choice_formset:
#                     if form.cleaned_data.get('DELETE'):
#                         continue  # Skip forms marked for deletion
#                     choice_text = form.cleaned_data.get('choice_text')
#                     if choice_text:
#                         choice = form.save(commit=False)
#                         choice.poll = poll
#                         valid_choices.append(choice)

#                 # Validate minimum number of choices
#                 if len(valid_choices) < 2:
#                     print(len(valid_choices))
#                     messages.error(request, 'Please provide at least two choices for the poll.')
#                     transaction.set_rollback(True)
#                 else:
#                     # Save valid choices
#                     for choice in valid_choices:
#                         choice.save()
#                     messages.success(request, 'Post with poll created successfully!')
#                     return redirect('forum:post_detail', pk=post.pk)
#         else:
#             messages.error(request, 'There was an error in your submission.')

#         return render(request, self.template_name, {
#             'post_form': post_form,
#             'poll_choice_formset': poll_choice_formset,
#         })





class PostDetailView(View):

    template_name = 'forum/post/post-detail.html'

    def get(self, request: HttpRequest, pk: int):

        try:
            post = Post.objects.get(id=pk)
            comments = PostComment.objects.filter(
                post=post).order_by('-time_created')

            comment_form = PostCommentForm()
            reply_form = PostCommentReplyForm()

            comment_count = comments.count()

            # Check if each comment is liked by the user
            comments_with_like_status = []
            for comment in comments:
                is_liked_by_user = CommentLike.objects.filter(
                    comment=comment, user=request.user, is_liked=True).exists()
                print(comment.comment_likes.filter(is_liked=True).count())

                comments_with_like_status.append({
                    'comment': comment,
                    'is_liked_by_user': is_liked_by_user,
                    # Fetch total likes
                    'total_likes': comment.comment_likes.filter(is_liked=True).count()
                })

            print(comments_with_like_status)

            # Check if the post is liked by the current user
            is_liked_by_user = post.likes.filter(
                user=request.user, is_liked=True).exists()
            print(is_liked_by_user)

            return render(request, self.template_name, {
                "post": post,
                "comment_form": comment_form,
                "comments_with_like_status": comments_with_like_status,
                "is_liked_by_user": is_liked_by_user,  # Pass to the template
                "comment_count": comment_count,
                'reply_form': reply_form
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

        return render(request, 'forum/post/post_detail', {"post": post, "comment_form": form})


class PostReplyView(View):

    def post(self, request: HttpRequest, comment_id: int):

        form = PostCommentReplyForm(request.POST)

        comment = PostComment.objects.get(id=comment_id)

        if form.is_valid():

            comment_body = form.cleaned_data.get('reply_body')
            author = request.user

            reply = form.save(commit=False)

            # Add other fields
            reply.author = author
            reply.comment = comment

            # Save comment

            reply.save()
            messages.success(request, 'Replied successfully')

            return redirect(reverse_lazy('forum:post_detail', args=[comment.post.pk]))

        return render(request, 'forum/post/post_detail', {"post": comment.post, "comment_form": form})


class LikePostView(View):

    def post(self, request, post_id):

        post = get_object_or_404(Post, id=post_id)
        user = request.user

        # Get or create a PostLikes object
        post_like, created = PostLikes.objects.get_or_create(
            user=user, post=post)

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


class LikeCommentView(View):

    def post(self, request, comment_id):
        comment = get_object_or_404(PostComment, id=comment_id)
        user = request.user

        # Check if the user has already liked the comment
        comment_like, created = CommentLike.objects.get_or_create(
            user=user, comment=comment)

        if not created:
            # Toggle the 'is_liked' field if the like object already exists
            comment_like.is_liked = not comment_like.is_liked
            comment_like.save()
        else:
            # If it's a new like object, mark it as liked
            comment_like.is_liked = True
            comment_like.save()

        # Return the current like status and total likes for the comment
        total_likes = CommentLike.objects.filter(
            comment=comment, is_liked=True).count()
        print(total_likes)

        return JsonResponse({
            'liked': comment_like.is_liked,
            'total_likes': total_likes,
        })


class CommunityView(View):

    template_name = 'forum/community/community-page.html'

    def get(self, request: HttpRequest, community_id: int):

        try:
            communities = PostCommunity.objects.all()
            community = PostCommunity.objects.get(id=community_id)
            posts = Post.objects.filter(
                community=community).order_by("-time_created")

            # Create a list of posts with their like status for the current user
            posts_with_like_status = []
            for post in posts:
                is_liked_by_user = PostLikes.objects.filter(
                    post=post, user=request.user, is_liked=True).exists()
                posts_with_like_status.append({
                    'post': post,
                    'is_liked_by_user': is_liked_by_user
                })

            return render(request, self.template_name, {
                "posts_with_like_status": posts_with_like_status,
                "community": community,
                "communities": communities,
            })

        except PostCommunity.DoesNotExist:
            return render(request, self.template_name, {"error": "Community does not exist"})


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'forum/profile/change_password.html'

    def get_success_url(self):
        # Return the URL for the profile view with the correct username
        return reverse_lazy('forum:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        messages.success(
            self.request, "Your password was successfully updated!")
        # Important to avoid logging the user out
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class ProfileView(View):

    template_name = 'forum/profile/profile-page.html'

    def get(self, request: HttpRequest, username: str):

        user_posts = Post.objects.filter(
            author=request.user).order_by("-time_created")
        user_comments = PostComment.objects.filter(author=request.user)
        user_commented_posts = Post.objects.filter(
            comments__author=request.user).distinct().order_by("-time_created")
        profile_form = UpdateProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(
            user=request.user)  # Use the custom form

        return render(request, self.template_name, {"posts": user_posts, "commented_posts": user_commented_posts,
                                                    "profile_form": profile_form, "password_form": password_form})

    def post(self, request, username):
        profile_form = UpdateProfileForm(instance=request.user, data=request.POST)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(reverse_lazy('forum:profile', kwargs={'username': request.user.username}))

        elif 'change_password' in request.POST and password_form.is_valid():
            print("Hello")
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, "Password changed successfully!")
            return redirect(reverse_lazy('forum:profile', kwargs={'username': request.user.username}))

        # If the forms are not valid, they will re-render with the errors
        return render(request, self.template_name, {
            'profile_form': profile_form,
            'password_form': password_form
        })
