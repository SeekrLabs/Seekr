from django.db import models
from datetime import date
from PIL import Image, ImageDraw
from global_variables import linkedin
import numpy as np
from profiles.models import Profile

class Posting(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    title = models.CharField(max_length=64, blank=True)
    company = models.CharField(max_length=64, blank=True)

    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=8, blank=True)
    country = models.CharField(max_length=16, blank=True)

    source = models.CharField(max_length=16, blank=True)
    date_posted = models.DateField(default=date.today)
    url = models.URLField(blank=True)
    vector = models.BinaryField()
    description = models.CharField(max_length=256, blank=True)
    image_url = models.URLField(blank=True)

    search_title = models.CharField(max_length=16, blank=True)
    num_employees = models.IntegerField(null=True)

    # logo = models.URLField(default='')
    
    def generate_vector(self, num_profiles):
        return True
        profiles = linkedin.get_profiles(self.company, self.search_title, num_profiles)
        posting_vector = np.zeros(Profile.VECTOR_LEN, dtype=np.float32)
        num_added_profiles = 0
        for p in profiles:
            exp_start_date = p.get_experience_start_date(self.company, self.search_title)
            if exp_start_date:
                posting_vector = np.add(posting_vector, p.to_vector(exp_start_date))
                num_added_profiles += 1
        posting_vector = np.divide(posting_vector, num_added_profiles)
        
        if num_added_profiles > 5:
            self.vector = posting_vector.dumps()
            self.num_employees = num_added_profiles
            return True
        return False

    def get_image_url(self):
        if self.image_url is None:
            image = self.generate_image()
            self.image_url = self.save_image(image)
        return self.image_url

    def generate_image(self):
        # title = self.tile to access parameters
        # each posting has company logo, job title, experience level, location, and posting link
        #img = Image.new('RGB', (570, 430), color = (255, 255, 255))
        if self.logo is None: 
            logo = default_logo
            self.logo = self.save_logo(logo)
        img = Image.open(self.logo_url) 
        #i'm not entirely sure this will work lmao 

        #draw the image 
        draw = ImageDraw.Draw(img)
        draw.line((0, 0) + img.size, fill=(0,0,0))
        draw.text((0, 0) + img.size, self.title, fill=(0,0,0))
        draw.text((0, 0) + img.size + 20, self.company + "• Full Time", fill = (0,0,0))
        draw.line((0, 0) + img.size + 60, fill = (0,0,0))
        url = id + company + title + ".jpg"
        img.save(url)
        #pass

    def save_image(self, image):
        """ 
        Save to Amazon S3
  
        Parameters: 
            image (TBD):
          
        Returns:
            image_url (string): a publically access url string
        """
        pass

    def __str__(self):
        return '{:39}{:24}{:24}{}\t{:70}'.format(self.title[:35], self.company[:20],
                self.city[:20], self.date_posted, self.url[:70])