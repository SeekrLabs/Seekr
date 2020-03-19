from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile
from postings.models import Posting
from datetime import date, timedelta
import numpy as np
import logging

logger = logging.getLogger('app')

class MessengerUser(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    profile = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    desired_location = models.CharField(max_length=32, blank=True)
    desired_title = models.CharField(max_length=64, blank=True)
    profile_pic_url = models.CharField(max_length=256, blank=True)
    gender = models.CharField(max_length=16, blank=True)

    saved_postings = models.ManyToManyField(Posting)
    clicked_postings = models.ManyToManyField(Posting, related_name="clicks")


    def compute_similarity(self, posting):
        """ Computes similarity score between job posting and profile

        Parameters:
            posting (Posting): a job posting

        Returns:
            cos_sim (Float): a value representing how different the user is to the existing
                employees of the job posting, the higher the value, the it will be
                recommended
        """
        today = date.today()
        my_vec = self.profile.to_vector(today)
        posting_vec = np.loads(posting.vector)

        cos_sim = np.dot(my_vec, posting_vec) \
                / (np.linalg.norm(my_vec) * np.linalg.norm(posting_vec))

        return cos_sim

    def get_postings(self, title, location, offset):
        # postings = self.filter_postings(title, location)
        # postings.sort(key=self.compute_similarity)
        
        # return postings[offset*10:offset*10+10]
        return self.rank_postings(
            self.filter_postings(title, location)
        )[offset*10:offset*10+10]

    def filter_postings(self, title, location):
        """Filters postings given title and location

        Parameters:
            title (str): the job title that user seeks
            location (str): the city at which the user seeks

        Returns:
            base_queryset (QuerySet): a set of filtered postings by title, city and date
        """
        # Title
        title_words = title.split()
        base_queryset = Posting.objects.all()
        for word in title_words:
            base_queryset = base_queryset.filter(title__icontains=word)
        
        # Location
        base_queryset = base_queryset.filter(city__icontains=location)

        # New jobs
        last_day = date.today() - timedelta(days=30)
        base_queryset = base_queryset.filter(date_posted__gt = last_day)

        return base_queryset

    def rank_postings(self, postings):
        has_vector = postings.exclude(num_employees=-1)
        no_vector = postings.filter(num_employees=-1)

        scores = sorted([(self.compute_similarity(p), p) for p in has_vector], reverse=True)
        postings_with_vectors = [p[1] for p in scores]
        logger.info("Ranked {} postings with vectors, {} without vectors".format(
            len(postings_with_vectors), len(no_vector)))
            
        return postings_with_vectors + list(no_vector.order_by('date_posted'))