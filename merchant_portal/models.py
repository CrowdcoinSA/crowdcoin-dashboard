from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile_user')
	api_key = models.CharField(max_length=100,null=True, blank=True)

	def __unicode__(self):
		return '%s'% self.user.username

def create_user_profile(sender, instance, created, ** kwargs):
	if instance:
		try:
			user = UserProfile.objects.get(user__username=instance.username)
		except UserProfile.DoesNotExist:
			# Create a new user. There's no need to set a password
			# because only the password from settings.py is checked.
			user = UserProfile.objects.create(user=instance)		

post_save.connect(create_user_profile, sender=User)