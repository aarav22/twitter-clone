from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from PIL import Image

import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default=f'https://avatars.dicebear.com/api/adventurer/{id_generator()}.svg', upload_to='display_pics')

    def __str__(self):
        return f'{self.user.username}'

    def getFollowers(self):
        return FollowAction.objects.filter(follow_user=self.user).count()

    def getFollowing(self):
        return FollowAction.objects.filter(user=self.user).count()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()


class FollowAction(models.Model):
    user = models.ForeignKey(User, related_name='user',
                             on_delete=models.CASCADE)
    follow_user = models.ForeignKey(
        User, related_name='follow_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Setup(models.Model):
    api_key = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200)
    choices = [("email", "Email"), ("phone_number_sms", "Phone")]
