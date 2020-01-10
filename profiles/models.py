from django.db import models
import numpy as np
import sys

if any(command in sys.argv for command in ['runserver', 'shell', 'test']):
    from .schools import School, StudyField

class Profile(models.Model):
    name = models.CharField(max_length=128, default='', blank=True)
    location = models.DateField(max_length=64, blank=True)

    def to_vector(self, date):
        pass


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=128, default='')
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
        """
        res = []

        school_vec = School(self.school_name).to_vector()
        gpa = [self.gpa]
        years_to_complete_degree = [round((self.end_date - self.start_date).days / 365)]
        years_since_graduation = [round((profile_simulation_date - self.end_date).days / 365)]
        field_of_study = StudyField(self.field_of_study).to_vector()

        return school_vec + gpa + years_to_complete_degree + years_since_graduation + field_of_study