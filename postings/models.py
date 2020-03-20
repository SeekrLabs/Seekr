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
    
    def generate_vector(self, num_profiles):
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
        if num_added_profiles > 3:
            posting_vector = np.divide(posting_vector, num_added_profiles)
            self.vector = posting_vector.dumps()
            return True

        logger.info("No profiles match.")
        return False

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
        bucket = "tempBucketString"
        
        #Check if url is already in s3
        imageFilename = company + ".png"
        s3UrlAttempt = "https://" + bucket + ".s3-us-east-1.amazonaws.com/" + imageFilename
        #Use url to check if already in s3
        isPresent = True
        
        s3Resource = boto3.resource('s3')
        try:
            s3Resource.Object(bucket, imageFilename).load()
        except botocore.exceptions.ClientError as error:
            isPresent = False
        
        if isPresent:
            return s3UrlAttempt
        
        #Get company autocomplete and values
        url = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + company
        searchResult = urllib.request.urlopen(url)
        data = searchResult.read()
        encodedData = searchResult.info().get_content_charset('utf-8')
        resultingData = json.loads(data.decode(encodedData))
        
        #Create byte buffer representing logo image
        #In the new form of upload, you need to do Image.open(byteBuffer) to access the image itself
        item = resultingData[0]
        clearbitURL = item["logo"]
        logoResponse = requests.get(clearbitURL)
        byteBuffer = BytesIO(logoResponse.content)
        
        #Upload to S3
        s3.upload_fileobj(byteBuffer, bucket, imageFilename)
        
        s3Url = "https://" + bucket + ".s3-us-east-1.amazonaws.com/" + imageFilename
        
        return s3Url

    def get_image_url(self):
        if self.image_url is None:
            image = self.generate_image()
            self.image_url = self.save_image(image)
        return self.image_url

    def generate_image(self):
        # use URL of logo image and get it
        # response = requests.get(self.image_url)

        # using a filler url for now since waiting on Russell's code 
        load_logo()

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
        titlelines = textwrap.wrap(self.title, width = 20)
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
        
        # call function to save to s3 
        gen_image_url = save_image(self, background)

        # do a check to see if has been pushed by searching s3 
        bucket = "generatedImageJobCardBucket"
        generatedURL = self.id + ".png"
        s3URL = "https://" + bucket + ".s3-us-east-1.amazonaws.com/" + generatedURL

        isPresent = True
        
        s3Resource = boto3.resource('s3')
        try:
            s3Resource.Object(bucket, imageFilename).load()
        except botocore.exceptions.ClientError as error:
            isPresent = False
        
        if isPresent:
            # delete local after saving
            os.remove(tempname)
            return gen_image_url

        gen_image_url = save_image(self, background)    
        return gen_image_url
        #pass

    def save_image(self, image):
        """ 
        Save to Amazon S3
  
        Parameters: 
            image (TBD):
          
        Returns:
            image_url (string): a publically access url string
        """
        
        # will only save to s3 when an image has been generated 
        # Declare Bucket to save generated image cards to
        bucket = "generatedImageJobCardBucket"
        
        # Create url is already in s3
        generatedURL = self.id + ".png"
        s3URL = "https://" + bucket + ".s3-us-east-1.amazonaws.com/" + generatedURL
        s3Resource = boto3.resource('s3')

        #Create byte buffer from image passed through the function
        byteBuffer = BytesIO(image)
        
        #Upload to S3
        s3.upload_fileobj(byteBuffer, bucket, generatedURL)
        
        s3Url = "https://" + bucket + ".s3-us-east-1.amazonaws.com/" + imageFilename
        
        return s3Url

    def __str__(self):
        return '{:39}{:24}{:24}{}\t{:70}'.format(self.title[:35], self.company[:20],
                self.city[:20], self.date_posted, self.url[:70])