from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile
from postings.models import Posting

class MessengerUser(models.Model):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    # user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    desired_location = models.CharField(max_length=32, blank=True)
    desired_title = models.CharField(max_length=64, blank=True)
    profile_pic_url = models.CharField(max_length=256, blank=True)
    gender = models.CharField(max_length=16, blank=True)

    def get_postings(self, title, location, offset):
        return self.sort_postings(
            self.filter_postings(title, location)
        )[offset*10:offset*10+10]

    def filter_postings(self, title, location):
        # Title
        title_words = title.split()
        base_queryset = Posting.objects.all()
        for word in title_words:
            base_queryset = base_queryset.filter(title__icontains=word)
        
        # Location
        base_queryset = base_queryset.filter(location__icontains=location)

        return base_queryset

    def sort_postings(self, postings):
        return postings.order_by('date_posted')