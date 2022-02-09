from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from posts.models import Post, Like
from intellectuals.models import FollowAction, UserProfile
import sys
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
# Create your views here.

PAGINATION_COUNT = 3


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']
    template_name = 'post_new.html'
    success_url = '/home'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Add a new post'
        return data


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'user_posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATION_COUNT

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == '', file=sys.stderr)

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (FollowAction.objects.filter(user=logged_user,
                                                follow_user=visible_user).count() == 0)
        data = super().get_context_data(**kwargs)

        data['user_profile'] = visible_user
        data['can_follow'] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = FollowAction.objects.filter(user=request.user,
                                                    follow_user=self.visible_user())

            if 'follow' in request.POST:
                new_relation = FollowAction(
                    user=request.user, follow_user=self.visible_user())
                if follows_between.count() == 0:
                    new_relation.save()
            elif 'unfollow' in request.POST:
                if follows_between.count() > 0:
                    follows_between.delete()

        return self.get(self, request, *args, **kwargs)


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author')\
            .annotate(author_count=Count('author'))\
            .order_by('-author_count')[:6]

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())
        data['like'] = Like.objects.all()
        data['all_users'] = all_users
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        user = self.request.user
        qs = FollowAction.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')


class FollowersListView(ListView):
    model = FollowAction
    template_name = 'follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return FollowAction.objects.filter(follow_user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'
        return data


class FollowsListView(ListView):
    model = FollowAction
    template_name = 'follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return FollowAction.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'follows'
        return data


@login_required
def postpreference(request, postid, userpreference):

    if request.method == "POST":
        eachpost = get_object_or_404(Post, id=postid)

        obj = ''

        valueobj = ''

        try:
            obj = Like.objects.get(user=request.user, post=eachpost)

            valueobj = obj.value  # value of userpreference

            valueobj = int(valueobj)

            userpreference = int(userpreference)

            if valueobj != userpreference:
                obj.delete()

                upref = Like()
                upref.user = request.user

                upref.post = eachpost

                upref.value = userpreference

                if userpreference == 1 and valueobj != 1:
                    eachpost.likes += 1
                    eachpost.dislikes -= 1
                elif userpreference == 2 and valueobj != 2:
                    eachpost.dislikes += 1
                    eachpost.likes -= 1

                upref.save()

                eachpost.save()

                context = {'eachpost': eachpost,
                           'postid': postid}

                return redirect('home')

            elif valueobj == userpreference:
                obj.delete()

                if userpreference == 1:
                    eachpost.likes -= 1
                elif userpreference == 2:
                    eachpost.dislikes -= 1

                eachpost.save()

                context = {'eachpost': eachpost,
                           'postid': postid}

                return redirect('home')

        except Like.DoesNotExist:
            upref = Like()

            upref.user = request.user

            upref.post = eachpost

            upref.value = userpreference

            userpreference = int(userpreference)

            if userpreference == 1:
                eachpost.likes += 1
            elif userpreference == 2:
                eachpost.dislikes += 1

            upref.save()

            eachpost.save()

            context = {'eachpost': eachpost,
                       'postid': postid}

            return redirect('home')

    else:
        eachpost = get_object_or_404(Post, id=postid)
        context = {'eachpost': eachpost,
                   'postid': postid}

        return redirect('home')


@api_view(['GET', 'POST', 'DELETE'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()

        title = request.query_params.get('title', None)
        if title is not None:
            posts = posts.filter(title__icontains=title)

        posts_serializer = PostSerializer(posts, many=True)
        return JsonResponse(posts_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        post_data = JSONParser().parse(request)
        post_serializer = PostSerializer(data=post_data)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse(post_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Post.objects.all().delete()
        return JsonResponse({'message': '{} Posts were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)
