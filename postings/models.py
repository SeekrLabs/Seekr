from django.db import models
from datetime import date

class Posting(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    title = models.CharField(max_length=64, default='')
    company = models.CharField(max_length=64, default='')
    location = models.CharField(max_length=64, default='')
    source = models.CharField(max_length=16, default='')
    date_posted = models.DateField(default=date.today)
    url = models.URLField(default='')
    vector = models.CharField(max_length=2048, default='')
    description = models.CharField(max_length=256, default='')
    image_url = models.URLField(blank=True)

    def get_image_url(self):
        if self.image_url is None:
            image = self.generate_image()
            self.image_url = self.save_image(image)
        return self.image_url

    def generate_image(self):
        # title = self.tile to access parameters
        pass

    def save_image(self, image):
        """ 
        Save to Amazon S3
  
        Parameters: 
            image (TBD):
          
        Returns:
            image_url (string): a publically access url string
        """
        pass