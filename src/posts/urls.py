from django.urls import path
from .views import (
    PostListView,
    PostCreateView,
    FollowsListView,
    FollowersListView,
    UserPostListView,
    postpreference,
    post_list)
from .import views

urlpatterns = [
    path('home/', PostListView.as_view(), name='home'),
    path('user/<str:username>/followers', FollowersListView.as_view(), name='user-followers'),
    path('post/<int:postid>/preference/<int:userpreference>', postpreference, name='postpreference'),
    path('user/<str:username>/follows', FollowsListView.as_view(), name='user-follows'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),

]
