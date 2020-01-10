from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile
from postings.models import Posting

class MessengerUser(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    desired_location = models.CharField(max_length=32, blank=True)
    desired_job_title = models.CharField(max_length=64, blank=True)
    profil_pic_url = models.CharField(max_length=256, blank=True)
    gender = models.CharField(max_length=16, blank=True)