from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=128)
    location = models.DateField(max_length=64)

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField()

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    institution = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField()