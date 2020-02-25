from django.db import models
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from global_variables import linkedin
import numpy as np
from profiles.models import Profile
import requests
import textwrap
from io import BytesIO
import urllib.request
import json
import boto3
import os

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
        """Generates a averaged vector of the job postings existing employees
  
        Parameters: 
            num_profiles (int): number of profiles
            
        Returns:
            (boolean): if generation was successful, fails if less than 5 existing
                employees
        """
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
        
        # use URL of logo image and get it
        # response = requests.get(self.image_url)

        # using a filler url for now since waiting on Russell's code 
        response = requests.get("https://logo.clearbit.com/spotify.com")
        img = Image.open(BytesIO(response.content))
        
        # creating local variable storing full location 
        location = self.city + ", " + self.state

        # importing company logo and placing it on new Image 
        img_w, img_h = img.size
        background = Image.new('RGBA', (909, 476), (255, 255, 255, 255))
        bg_w, bg_h = background.size
        offset = (751, 30)
        background.paste(img, offset)

        # creating default font types 
        ftitle = 60
        fsub = 40
        fnorm = 28
        fnt_title = ImageFont.truetype('/Library/Fonts/Arial.ttf', ftitle)
        fnt_sub = ImageFont.truetype('/Library/Fonts/Arial.ttf', fsub)
        fnt_norm = ImageFont.truetype('/Library/Fonts/Arial.ttf', fnorm)

        # creating default margin sizes 
        left_margin, right_margin, top_margin, bottom_margin = 30,30,30,30
        spacing = 30
        line_space = 40
        
        # create variable to draw on the image and add text 
        d = ImageDraw.Draw(background)

        # Drawing text for job posting information 
        # draw text, Company Title 
        titlelines = textwrap.wrap(position, width = 20)
        start_height = top_margin
        for titleline in titlelines:
            width, height = fnt_title.getsize(titleline)
            d.text((left_margin, start_height), titleline, font=fnt_title,fill=(64,64,64))
            start_height += 56

        # draw text, Position Title
        pos_height = top_margin + 128 + line_space
        d.text((left_margin, pos_height), self.company, font=fnt_sub, fill=(0,120,255))

        # draw text, Location
        loc_height = pos_height + 20 + line_space
        d.text((left_margin, loc_height), location, font=fnt_norm, fill=(64,64,64))

        # draw description 
        lines = textwrap.wrap(self.description, width = 60)
        start_height = loc_height + 10 + line_space
        for line in lines:
            width, height = fnt_norm.getsize(line)
            d.text((left_margin, start_height), line, font=fnt_norm,fill=(64,64,64))
            start_height += spacing

        tempname = self.id + '.png'
        background.save(tempname)
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
        return "%s %s %s" % (self.company, self.title, self.date_posted)