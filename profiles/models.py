from django.db import models
import numpy as np
import sys
from .representations import ExperienceRepresentation, SkillRepresentation
from utils.glove import glove
from constants import *
from .schools import School


class Profile(models.Model):
    name = models.CharField(max_length=128, default='', blank=True)
    location = models.CharField(max_length=64, blank=True)
    profile_url = models.CharField(max_length = 200, default = "")

    def username_validator(username):
        for c in username:
            if not c.isalnum():
                print("Invalid username format")
                return False
        if len(username) < 3 or len(username) > 100:
            print("Invalid username format")
            return False
        return True
        
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

        exp_repr = ExperienceRepresentation(PREV_YEARS_LOOKUP)
        for e in self.experience_set.all():
            exp_repr.add_experience(e, profile_simulation_date)
        experience_vector = exp_repr.to_vector()

        skills_repr = SkillRepresentation(profile_simulation_date)
        for e in self.experience_set.all():
            skills_repr.add_text(e.description, e.end_date)
        for edu in self.education_set.all():
            skills_repr.add_text(edu.description, edu.end_date)
        skills_vector = skills_repr.to_vector()

        return education_vector + experience_vector + skills_vector
        
    def education_to_vector(self, profile_simulation_date):
        if len(self.education_set.all()) == 0:
            return [0] * EDUCATION_VECTOR_LEN
        else:
            return self.education_set.all()[0].to_vector(profile_simulation_date)


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=128, default='')
    title = models.CharField(max_length=32, default='')
    description = models.CharField(max_length=128, default='')
    start_date = models.DateField(default='')
    end_date = models.DateField(default='')
    is_current = models.BooleanField()

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=128, default='')  
    degree = models.CharField(max_length=64, default='')
    field_of_study = models.CharField(max_length=64, default='')
    description = models.CharField(max_length=128, default='', blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0, blank=True, null=True)

    start_date = models.DateField(default='')
    end_date = models.DateField(default='', blank=True)
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
                        [school_vec, gpa, years_to_complete_degree, years_since_graduation,
                         field_of_study (3 * word_embedding)]
        """
        school_vec = School(self.school_name).to_vector()
        gpa = [self.gpa] if self.gpa else [0]
        years_to_complete_degree = [round((self.end_date - self.start_date).days / 365)]
        years_since_graduation = [0] if self.is_current else [round((profile_simulation_date - self.end_date).days / 365)]
        field_of_study = glove.get_string_embedding(self.field_of_study, 3)

        return school_vec + gpa + years_to_complete_degree + years_since_graduation + field_of_study