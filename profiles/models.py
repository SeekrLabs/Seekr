from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=128, default='')
    location = models.DateField(max_length=64)
    vector = models.CharField(max_length=2048, default='')

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=128, default='')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField()

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    institution = models.CharField(max_length=128, default='')
    description = models.CharField(max_length=128, default='')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField()