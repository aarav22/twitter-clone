from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index),
    path('logout/', auth_views.LogoutView.as_view(template_name='index.html'), name='logout'),
    path('login/', views.login, name='login'),
    path('receive', views.receive)
]
