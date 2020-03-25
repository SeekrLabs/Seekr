from django.db import models
from datetime import date
from PIL import Image, ImageDraw
import urllib.request
import json
import boto3
import botocore
import os
from constants import *
from global_variables import s3
import requests
from io import BytesIO

import numpy as np
from profiles.models import Profile
import logging

logger = logging.getLogger('app')


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
    num_employees = models.IntegerField(default=-1)

    # logo = models.URLField(default='')
    
    def generate_vector(self, num_profiles, linkedin):
        """Generates a averaged vector of the job postings existing employees
  
        Parameters: 
            num_profiles (int): number of profiles
            
        Returns:
            (boolean): if generation was successful, fails if less than 5 existing
                employees
        """
        profiles = linkedin.get_profiles(self.company, self.search_title, num_profiles)

        posting_vector = np.zeros(Profile.VECTOR_LEN, dtype=np.float32)
        num_added_profiles = 0
        for p in profiles:
            exp_start_date = p.get_experience_start_date(self.company, self.search_title)
            if exp_start_date:
                posting_vector = np.add(posting_vector, p.to_vector(exp_start_date))
                num_added_profiles += 1
        
        self.num_employees = num_added_profiles
        if num_added_profiles >= 3:
            posting_vector = np.divide(posting_vector, num_added_profiles)
            self.vector = posting_vector.dumps()
            return True

        logger.info("No profiles match.")
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

    #Takes in a company name and bucket location for upload
    #and uploads the file to S3, and returns the s3 url
    def load_logo(self, company):
        """Loads a company logo based on company name

        Queries bitbucket api to find a logo from partial company names, and saves the logo url to s3. 

        Args:
            company (string): The company name to find the logo for

        Returns:
            Returns the URL that a user can query to get the logo from S3. 
        """
        
        
        #Declare Bucket to save to
        bucket = "seekr-company-logo-image"
        
        #Check if url is already in s3
        image_filename = company + ".png"
        s3_url_attempt = "https://" + bucket + ".s3.us-east-2.amazonaws.com/" + image_filename
        #Use url to check if already in s3
        is_present = True
        
        s3_resource = boto3.resource('s3')
        try:
            s3_resource.Object(bucket, image_filename).load()
        except botocore.exceptions.ClientError as error:
            is_present = False
        
        if is_present:
            return s3_url_attempt
        
        #Get company autocomplete and values
        url = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + company
        search_result = urllib.request.urlopen(url)
        data = search_result.read()
        encoded_data = search_result.info().get_content_charset('utf-8')
        resulting_data = json.loads(data.decode(encoded_data))
        
        #Create byte buffer representing logo image
        #In the new form of upload, you need to do Image.open(byteBuffer) to access the image itself
        item = resulting_data[0]
        clearbit_url = item["logo"]
        logo_response = requests.get(clearbit_url)
        byte_buffer = BytesIO(logo_response.content)
        
        #Upload to S3
        s3.upload_fileobj(byte_buffer, bucket, image_filename)
        
        s3Url = "https://" + bucket + ".s3.us-east-2.amazonaws.com/" + image_filename
        
        return s3Url
    
    def __str__(self):
        return '{:39}{:24}{:24}{}\t{:70}'.format(self.title[:35], self.company[:20],
                self.city[:20], self.date_posted, self.url[:70])
