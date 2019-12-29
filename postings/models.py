from django.db import models

class Posting(models.Model):
    title = models.CharField(max_length=64)
    time_posted = models.DateTimeField()
    url = models.URLField()
    vector = models.CharField(max_length=2048)
    text = models.CharField(max_length=4096)