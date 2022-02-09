from django.contrib import admin
from .models import Setup, UserProfile, FollowAction

# Register your models here.

admin.site.register(FollowAction)
admin.site.register(UserProfile)
admin.site.register(Setup)
