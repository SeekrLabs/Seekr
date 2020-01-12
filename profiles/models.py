from django.db import models
import numpy as np
import sys
from .experiences import ExperienceRepresentation
from config import glove
from constants import *

if any(command in sys.argv for command in ['runserver', 'shell', 'test']):
    from .schools import School

class Profile(models.Model):
    name = models.CharField(max_length=128, default='', blank=True)
    location = models.DateField(max_length=64, blank=True)

    def to_vector(self, profile_simulation_date):
        """ 
        Returns a numerical representation of profile
  
        Parameters: 
            profile_simulation_date (datetime.date): The date at which the profile is simulated.
                    A component represents years since graduation, so a profile vector is
                    dependent on the profile simulation date.
          
        Returns:
            List (int): representing the profile
        """
        education_vector = self.education_to_vector(profile_simulation_date)

        exp_repr = ExperienceRepresentation(profile_simulation_date.year)
        for e in self.experience_set.all():
            exp_repr.add_experience(e)
        experience_vector = exp_repr.to_vector()
        
    def education_to_vector(self, profile_simulation_date):
        if len(self.education_set) == 0:
            return [0] * EDUCATION_VECTOR_LEN
        else:
            return self.education_set[0].to_vector(profile_simulation_date)


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=128, default='')
    title = models.CharField(max_length=32, default='')
    description = models.CharField(max_length=128, default='')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField()

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=128, default='')  
    degree = models.CharField(max_length=64, default='')
    field_of_study = models.CharField(max_length=64, default='')
    description = models.CharField(max_length=128, default='', blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(blank=True)
    is_current = models.BooleanField()


    def to_vector(self, profile_simulation_date):
        """ 
        Returns a numerical representation of education
  
        Parameters: 
            profile_simulation_date (datetime.date): The date at which the profile is simulated.
                    A component represents years since graduation, so a profile vector is
                    dependent on the profile simulation date.
          
        Returns:
            List (int): representing the education
        """
        school_vec = School(self.school_name).to_vector()
        gpa = [self.gpa]
        years_to_complete_degree = [round((self.end_date - self.start_date).days / 365)]
        years_since_graduation = [round((profile_simulation_date - self.end_date).days / 365)]
        field_of_study = glove.get_string_embedding(self.field_of_study, 3)

        return school_vec + gpa + years_to_complete_degree + years_since_graduation + field_of_study