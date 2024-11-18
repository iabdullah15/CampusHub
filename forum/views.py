from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView

from django.db import transaction, models
from datetime import timedelta
from django.utils import timezone


from .models import PostCommunity, Post, PostComment, PostCategory, PostLikes, PostCommentReply, CommentLike, Poll, PollChoice, PollVote, Report
from .forms import PostForm, PostCommentForm, PostCommentReplyForm, UpdateProfileForm, CustomPasswordChangeForm, PollChoiceFormSet

from django.contrib.auth import update_session_auth_hash
from .helpers import ask_assistant, moderate_post, moderate_img
from user.models import CustomUser
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(View):

    template_name = "forum/home/home-v2.html"

    def get(self, request: HttpRequest):

        if request.user.is_authenticated:

            communities = PostCommunity.objects.all().order_by('community_name')
            all_posts = Post.objects.all().order_by("-time_created")

            # Create a list of posts with their like status (Current user)
            posts_with_like_status = []
            for post in all_posts:

                is_liked_by_user = PostLikes.objects.filter(
                    post=post, user=request.user, is_liked=True).exists()
                posts_with_like_status.append({
                    'post': post,
                    'is_liked_by_user': is_liked_by_user
                })

            return render(request, self.template_name, {
                'posts_with_like_status': posts_with_like_status,
                'communities': communities,
            })

        else:
            return redirect(reverse_lazy('user:sign-in'))


class PostSearchView(View):

    template_name = 'forum/post/post-search.html'

    def get(self, request):

        communities = PostCommunity.objects.all().order_by('community_name')
        posts = Post.objects.all().order_by("-time_created")

        # Create a list of posts with their like status (Current user)
        posts_with_like_status = []

        query = request.GET.get('q')

        if query:
            # Filter posts by checking if the query is in the title or body
            posts = posts.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            )

        for post in posts:

            is_liked_by_user = PostLikes.objects.filter(
                post=post, user=request.user, is_liked=True).exists()
            posts_with_like_status.append({
                'post': post,
                'is_liked_by_user': is_liked_by_user
            })

        return render(request, self.template_name, {
            'posts_with_like_status': posts_with_like_status,
            'communities': communities,
            'query': query
        })


class CreatePostView(View):

    template_name = "forum/post/create-post.html"

    def post(self, request: HttpRequest):

        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            community = form.cleaned_data.get('community')
            title = form.cleaned_data.get('title')
            body = form.cleaned_data.get('body')
            image = form.cleaned_data.get('image')

            post_category = PostCommunity.objects.get(community_name=community)
            author = request.user

            # Check if the user is suspended
            if author.is_suspended and author.suspension_end_date:
                if timezone.now() < author.suspension_end_date:
                    messages.error(
                        request,
                        f"Your account is suspended until {author.suspension_end_date.strftime(
                            '%Y-%m-%d %H:%M:%S')}. You cannot create new posts."
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

            # Image Moderation
            image_final_action = 'Accepted'
            image_nsfw_score = None

            if image:

                image_nsfw_score = moderate_img(image)
                print(f"nsfw_score: {image_nsfw_score}")

                if image_nsfw_score >= 0.5 and image_nsfw_score <= 0.6:

                    image_final_action = 'Warning Issued'
                    author.warning_count += 1
                    author.save()
                    post.image = image
                    messages.warning(
                        request,
                        f"Your post was rejected due to violating our community guidelines. Your account has been suspended until {
                            author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}."
                    )

                elif image_nsfw_score > 0.6:

                    image_final_action = 'Rejected'

            post.author = author
            post.moderation_status = final_action
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
                warning_attributes = [
                    attr for attr, action in actions.items() if action == 'Issue Warning']
                messages.warning(
                    request,
                    f"Your post has been created but contains content that may violate our guidelines: {
                        ', '.join(warning_attributes)}. Please review our community guidelines."
                )
                return redirect('forum:post_detail', pk=post.pk)

            elif final_action == 'Reject' or image_final_action == 'Rejected':
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
                        f"Your post was rejected due to violating our community guidelines. Your account has been suspended until {
                            author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}."
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


# class CreatePostWithPollView(View):

#     template_name = 'forum/post/create-poll.html'

#     def get(self, request: HttpRequest):
#         post_form = PostForm()
#         poll_choice_formset = PollChoiceFormSet(
#             queryset=PollChoice.objects.none())
#         return render(request, self.template_name, {
#             'post_form': post_form,
#             'poll_choice_formset': poll_choice_formset,
#         })

#     def post(self, request):
#         post_form = PostForm(request.POST, request.FILES)
#         poll_choice_formset = PollChoiceFormSet(
#             request.POST,
#             queryset=PollChoice.objects.none()
#         )

#         if post_form.is_valid() and poll_choice_formset.is_valid():
#             author = request.user

#             # Check if the user is suspended
#             if author.is_suspended and author.suspension_end_date:
#                 if timezone.now() < author.suspension_end_date:
#                     messages.error(
#                         request,
#                         f"Your account is suspended until {author.suspension_end_date.strftime(
#                             '%Y-%m-%d %H:%M:%S')}. You cannot create new posts."
#                     )
#                     return redirect('forum:home')
#                 else:
#                     # Suspension period is over
#                     author.is_suspended = False
#                     author.suspension_end_date = None
#                     author.save()

#             # Extract and validate poll choices
#             choices = []
#             for form in poll_choice_formset:
#                 if form.cleaned_data.get('DELETE'):
#                     continue  # Skip forms marked for deletion
#                 choice_text = form.cleaned_data.get('choice_text')
#                 if choice_text:
#                     choices.append(choice_text)

#             # Validate minimum number of choices
#             if len(choices) < 2:
#                 messages.error(
#                     request, 'Please provide at least two choices for the poll.')
#                 return render(request, self.template_name, {
#                     'post_form': post_form,
#                     'poll_choice_formset': poll_choice_formset,
#                 })

#             # Format content for moderation
#             title = post_form.cleaned_data.get('title')
#             body = post_form.cleaned_data.get('body')
#             image = form.cleaned_data.get('image')

#             choices_content = '\n'.join(choices)
#             content = f'{title}\n\n{body}\n\nChoices:\n{choices_content}'

#             # Perspective API moderation
#             final_action, actions = moderate_post(post_content=content)

#             # Handle the final action
#             if final_action == 'Accept' or final_action == 'Issue Warning':
#                 with transaction.atomic():
#                     # Update user counts if necessary
#                     if final_action == 'Issue Warning':
#                         author.warning_count += 1
#                         author.save()

#                     # Save the post
#                     post = post_form.save(commit=False)
#                     post.author = author
#                     post.image = image if image else None
#                     post.moderation_status = final_action
#                     post.moderation_timestamp = timezone.now()
#                     post.save()

#                     # Create a poll linked to the post
#                     poll = Poll.objects.create(post=post)

#                     # Save valid choices
#                     for choice_text in choices:
#                         PollChoice.objects.create(
#                             poll=poll, choice_text=choice_text)

#                 if final_action == 'Issue Warning':
#                     warning_attributes = [
#                         attr for attr, action in actions.items() if action == 'Issue Warning']
#                     messages.warning(
#                         request,
#                         f"Your post has been created but contains content that may violate our guidelines: {
#                             ', '.join(warning_attributes)}. Please review our community guidelines."
#                     )
#                 else:
#                     messages.success(
#                         request, 'Post with poll created successfully!')

#                 return redirect('forum:post_detail', pk=post.pk)

#             elif final_action == 'Reject':
#                 # Increment user's rejection count and handle suspension
#                 with transaction.atomic():
#                     author.rejection_count += 1
#                     author.save()

#                     if author.rejection_count >= 5 and not author.is_suspended:
#                         author.is_suspended = True
#                         author.suspension_end_date = timezone.now() + timedelta(days=7)
#                         author.save()
#                         messages.error(
#                             request,
#                             f"Your post was rejected due to violating our community guidelines. Your account has been suspended until {
#                                 author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}."
#                         )
#                     else:
#                         messages.error(
#                             request,
#                             "Your post was rejected due to violating our community guidelines. Please review our community guidelines."
#                         )

#                 # Render the form again without any database operations
#                 return render(request, self.template_name, {
#                     'post_form': post_form,
#                     'poll_choice_formset': poll_choice_formset,
#                 })
#         else:
#             messages.error(request, 'There was an error in your submission.')

#         return render(request, self.template_name, {
#             'post_form': post_form,
#             'poll_choice_formset': poll_choice_formset,
#         })


class CreatePostWithPollView(View):

    template_name = 'forum/post/create-poll.html'

    def get(self, request: HttpRequest):
        post_form = PostForm()
        poll_choice_formset = PollChoiceFormSet(
            queryset=PollChoice.objects.none())
        return render(request, self.template_name, {
            'post_form': post_form,
            'poll_choice_formset': poll_choice_formset,
        })

    def post(self, request):
        post_form = PostForm(request.POST, request.FILES)
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
                        f"Your account is suspended until {author.suspension_end_date.strftime(
                            '%Y-%m-%d %H:%M:%S')}. You cannot create new posts."
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
                messages.error(
                    request, 'Please provide at least two choices for the poll.')
                return render(request, self.template_name, {
                    'post_form': post_form,
                    'poll_choice_formset': poll_choice_formset,
                })

            # Format content for moderation
            title = post_form.cleaned_data.get('title')
            body = post_form.cleaned_data.get('body')
            image = post_form.cleaned_data.get('image')
            print(f"Image : {image}")

            choices_content = '\n'.join(choices)
            content = f'{title}\n\n{body}\n\nChoices:\n{choices_content}'

            # Text Moderation
            final_action, actions = moderate_post(post_content=content)

            # Image Moderation
            image_final_action = 'Accepted'
            image_nsfw_score = None

            if image:
                image_nsfw_score = moderate_img(image)
                print(f"nsfw_score: {image_nsfw_score}")

                if image_nsfw_score >= 0.5 and image_nsfw_score <= 0.6:
                    image_final_action = 'Warning Issued'
                    author.warning_count += 1
                    author.save()
                elif image_nsfw_score > 0.6:
                    image_final_action = 'Rejected'

            # Decide on the overall action
            if final_action == 'Reject' or image_final_action == 'Rejected':
                # Handle rejection
                with transaction.atomic():
                    author.rejection_count += 1
                    author.save()

                    if author.rejection_count >= 5 and not author.is_suspended:
                        author.is_suspended = True
                        author.suspension_end_date = timezone.now() + timedelta(days=7)
                        author.save()
                        messages.error(
                            request,
                            f"Your post was rejected due to violating our community guidelines. Your account has been suspended until {
                                author.suspension_end_date.strftime('%Y-%m-%d %H:%M:%S')}."
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

            elif final_action == 'Accept' and image_final_action == 'Accepted':
                # Proceed with accepting the post
                with transaction.atomic():
                    # Save the post
                    post = post_form.save(commit=False)
                    post.author = author
                    post.image = image
                    post.moderation_status = final_action
                    post.moderation_timestamp = timezone.now()
                    post.save()

                    # Create a poll linked to the post
                    poll = Poll.objects.create(post=post)

                    # Save valid choices
                    for choice_text in choices:
                        PollChoice.objects.create(
                            poll=poll, choice_text=choice_text)

                    messages.success(
                        request, 'Post with poll created successfully!')

                return redirect('forum:post_detail', pk=post.pk)

            elif final_action == 'Issue Warning' or image_final_action == 'Warning Issued':
                # Handle issuing warning
                with transaction.atomic():
                    author.warning_count += 1
                    author.save()

                    # Save the post
                    post = post_form.save(commit=False)
                    post.author = author
                    post.image = image
                    post.moderation_status = 'Issue Warning'
                    post.moderation_timestamp = timezone.now()
                    post.save()

                    # Create a poll linked to the post
                    poll = Poll.objects.create(post=post)

                    # Save valid choices
                    for choice_text in choices:
                        PollChoice.objects.create(
                            poll=poll, choice_text=choice_text)

                    # Prepare warning messages
                    warning_messages = []
                    if final_action == 'Issue Warning':
                        warning_attributes = [
                            attr for attr, action in actions.items() if action == 'Issue Warning']
                        if warning_attributes:
                            warning_messages.append(
                                f"Your post contains content that may violate our guidelines: {
                                    ', '.join(warning_attributes)}."
                            )
                    if image_final_action == 'Warning Issued':
                        warning_messages.append(
                            "The image you uploaded may contain inappropriate content."
                        )

                    messages.warning(
                        request,
                        " ".join(warning_messages) +
                        " Please review our community guidelines."
                    )

                return redirect('forum:post_detail', pk=post.pk)
            else:
                # Default case, should not occur
                messages.error(
                    request,
                    "An unexpected error occurred. Please try again."
                )
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


class Vote(View):
    def post(self, request, post_id, poll_id):

        choice_id = request.POST.get('choice_id')
        print(f"CHOICE ID: {choice_id}")
        if not choice_id:
            return JsonResponse({'success': False, 'error': 'Choice ID is required'}, status=400)

        try:
            poll = Poll.objects.get(id=poll_id, post__id=post_id)
            choice = PollChoice.objects.get(id=choice_id, poll=poll)

            # Create or update the user's vote
            vote, created = PollVote.objects.get_or_create(
                user=request.user, poll=poll, defaults={'choice': choice})
            print(vote, created)
            if not created:
                vote.choice = choice
                vote.save()

            # Calculate percentages for each choice
            total_votes = PollVote.objects.filter(poll=poll).count()
            choices_data = []
            for poll_choice in poll.choices.all():
                choice_votes = PollVote.objects.filter(
                    poll=poll, choice=poll_choice).count()
                percentage = round((choice_votes / total_votes)
                                   * 100) if total_votes > 0 else 0
                choices_data.append(
                    {'choice_id': poll_choice.id, 'percentage': percentage})

            return JsonResponse({'success': True, 'choices': choices_data})

        except (Poll.DoesNotExist, PollChoice.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid poll or choice'}, status=400)


class PostDetailView(View):

    template_name = 'forum/post/post-detail.html'

    def get(self, request: HttpRequest, pk: int):

        context = {}
        communities = PostCommunity.objects.all()
        context.update({'communities':communities})

        try:
            post = Post.objects.get(id=pk)
            comments = PostComment.objects.filter(
                post=post).order_by('-time_created')
            print(pk)

            try:
                if post.poll:

                    poll = Poll.objects.get(post=post)
                    poll_choices = PollChoice.objects.filter(poll=poll)
                    poll_vote = None

                    context.update({"poll": poll})
                    context.update({"poll_choices": poll_choices})

                    try:
                        poll_vote = PollVote.objects.get(
                            poll=poll, user=request.user)

                    except:
                        poll_vote = None

                # Calculate the total votes for the poll
                    total_votes = PollVote.objects.filter(poll=poll).count()

                    # Calculate the percentage for each choice
                    poll_choices_with_percentages = []

                    for choice in poll_choices:

                        choice_votes = PollVote.objects.filter(
                            poll=poll, choice=choice).count()

                        if total_votes > 0:

                            choice_percentage = (
                                choice_votes / total_votes) * 100

                        else:

                            choice_percentage = 0
                        poll_choices_with_percentages.append({
                            'choice': choice,
                            'percentage': choice_percentage,
                        })

                    # Update context for poll details
                    context.update({
                        "poll": poll,
                        "poll_choices": poll_choices_with_percentages,
                        "user_vote": poll_vote
                    })
                    print(poll_vote.choice)
            except:
                None

            comment_form = PostCommentForm()
            reply_form = PostCommentReplyForm()

            comment_count = comments.count()

            # Check if each comment is liked by the user
            comments_with_like_status = []
            for comment in comments:
                is_liked_by_user = CommentLike.objects.filter(
                    comment=comment, user=request.user, is_liked=True).exists()
                # print(comment.comment_likes.filter(is_liked=True).count())

                comments_with_like_status.append({
                    'comment': comment,
                    'is_liked_by_user': is_liked_by_user,
                    # Fetch total likes
                    'total_likes': comment.comment_likes.filter(is_liked=True).count()
                })

            # Check if the post is liked by the current user
            is_liked_by_user = post.likes.filter(
                user=request.user, is_liked=True).exists()

            # Update context with post and comments data
            context.update({
                "post": post,
                "comment_form": comment_form,
                "comments_with_like_status": comments_with_like_status,
                "is_liked_by_user": is_liked_by_user,
                "comment_count": comment_count,
                'reply_form': reply_form
            })

            # print(context)

            return render(request, self.template_name, context=context)

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
        profile_form = UpdateProfileForm(
            instance=request.user, data=request.POST)
        password_form = CustomPasswordChangeForm(
            user=request.user, data=request.POST)

        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(reverse_lazy('forum:profile', kwargs={'username': request.user.username}))

        elif 'change_password' in request.POST and password_form.is_valid():
            print("Hello")
            user = password_form.save()
            # Keeps the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect(reverse_lazy('forum:profile', kwargs={'username': request.user.username}))

        # If the forms are not valid, they will re-render with the errors
        return render(request, self.template_name, {
            'profile_form': profile_form,
            'password_form': password_form
        })


class AdminPanel(View):

    def get(self, request: HttpRequest):

        if request.user.is_staff:

            # # Fetch all reported posts
            # reported_posts = Report.objects.select_related(
            #     'post', 'user').order_by('-timestamp')
            reported_posts = (
                Post.objects.annotate(report_count=models.Count('reports'))
                .filter(reports__isnull=False)
                .select_related('community', 'category')  # Fetch related fields
                .order_by('-report_count')  # Sort by report count
            )
            for i in reported_posts:
                print(i)
                print()

            reported_posts_count = reported_posts.count()
            post_count = Post.objects.all().count()
            print(reported_posts)
              # Fetch posts created in the last 24 hours
            last_24_hours = timezone.now() - timedelta(hours=24)
            recent_posts = Post.objects.filter(time_created__gte=last_24_hours).order_by('-time_created')

            return render(request, 'forum/admin/admin-panel.html', {'reported_posts': reported_posts, 
                                                                    'reported_posts_count': reported_posts_count, 
                                                                    'post_count': post_count,
                                                                    'recent_posts': recent_posts,})

        else:

            messages.error(
                request, message="You are not authorized to access the Admin Panel. To request access, please contact the relevant mods/admins")
            return redirect(reverse_lazy('forum:home'))


class ViewReports(View):
    
    def get(self, request:HttpRequest, post_id):
        
        post = Post.objects.get(id=post_id)
        reports = Report.objects.filter(post=post)
        
        return render(request, 'forum/admin/view-reports.html', {"post": post, "reports": reports})
        



class DeletePost(LoginRequiredMixin, View):

    login_url = reverse_lazy("user:sign-in")
    redirect_field_name = None

    def post(self, request: HttpRequest, post_id):

        try:
            post = Post.objects.get(id=post_id).delete()
            messages.success(
                request, "Your post has been sucessfully deleted.")
            return redirect(reverse_lazy('forum:profile', kwargs={'username': request.user.username}))
        except:
            messages.error(
                request, "There was an error with the request. Please try again later.")
            return redirect(reverse_lazy('forum:profile', kwargs={'username': request.user.username}))
        
        
        
class DisregardReports(View):
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        Report.objects.filter(post=post).delete()
        messages.success(request, "All reports have been disregarded.")
        return redirect(reverse_lazy('forum:admin_panel'))




class ReportPost(LoginRequiredMixin, View):
    login_url = reverse_lazy("user:sign-in")
    redirect_field_name = None

    def post(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)

        # Debugging: Check incoming data
        print(f"Post ID: {post.id}, User: {request.user.username}")

        if Report.objects.filter(post=post, user=request.user).exists():
            print(f"User {request.user.username} has already reported the post {
                  post.title}.")
            return JsonResponse({"success": False, "message": "You have already reported this post."}, status=400)

        reason = request.POST.get('reason', 'Inappropriate Content')
        comment = request.POST.get('comment', '').strip()

        # Debugging: Log the report details
        print(f"Creating report with reason: {reason}, comment: {comment}")

        # Create the report
        Report.objects.create(post=post, user=request.user,
                              reason=reason, comment=comment)

        return JsonResponse({"success": True, "message": "Report submitted successfully."})
