from django.db import models
from datetime import date
from PIL import Image, ImageDraw, ImageFont
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
import requests
import textwrap
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
        if self.image_url == "":
            self.image_url = self.generate_image()
        return self.image_url

    def generate_image(self):
        # use URL of logo image and get it
        # response = requests.get(self.image_url)

        # creating local variable storing full location 
        location = self.city + ", " + self.state

        # importing company logo and placing it on new Image 
        background = Image.new('RGBA', (909, 476), (255, 255, 255, 255))
        bg_w, bg_h = background.size

        # grab logo url using compnay name from s3 bucket
        logo_url = self.load_logo()
        if logo_url:
            # load the image using the s3 url
            try:
                response = requests.get(logo_url)
                logger.debug("Issued GET request for %s with response code %d", logo_url, response.status_code)
                img = Image.open(BytesIO(response.content))
                offset = (751, 30)
                background.paste(img, offset)
            except:
                logger.info("Could not get the logo for posting %s", self.id)

        # creating default font types 
        ftitle = 60
        fsub = 40
        fnorm = 28
        fnt_title = ImageFont.truetype('data/fonts/Arial.ttf', ftitle)
        fnt_sub = ImageFont.truetype('data/fonts/Arial.ttf', fsub)
        fnt_norm = ImageFont.truetype('data/fonts/Arial.ttf', fnorm)

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
        title_line_count = 1
        for titleline in titlelines:
            width, height = fnt_title.getsize(titleline)
            d.text((left_margin, start_height), titleline, font=fnt_title,fill=(64,64,64))
            start_height += 56
            title_line_count += 1
            if title_line_count > 2: 
                break

        # draw text, Position Title
        pos_height = top_margin + 128 + line_space
        d.text((left_margin, pos_height), self.company, font=fnt_sub, fill=(0,120,255))

        # draw text, Location
        loc_height = pos_height + 20 + line_space
        d.text((left_margin, loc_height), location, font=fnt_norm, fill=(64,64,64))

        # draw description 
        lines = textwrap.wrap(self.description, width = 60)
        start_height = loc_height + 10 + line_space
        desc_line_count = 1
        for line in lines:
            width, height = fnt_norm.getsize(line)
            d.text((left_margin, start_height), line, font=fnt_norm,fill=(64,64,64))
            start_height += spacing
            desc_line_count += 1
            if desc_line_count > 5:
                break

        tempname = self.id + '.png'
        gen_image_url = self.save_image_s3(background, tempname)
        
        return gen_image_url

    def save_image_s3(self, image, filename):
        """ 
        Save to Amazon S3
        Parameters: 
            image (TBD):
        Returns:
            image_url (string): a publically access url string
        """
        # will only save to s3 when an image has been generated 
        # Declare Bucket to save generated image cards to
        bucket = "seekr-job-posting-image-card"
        
        # Create url is already in s3
        generatedURL = self.id + ".png"

        byteBuffer = BytesIO()
        image.save(byteBuffer, 'PNG')
        byteBuffer.seek(0)
        
        s3.upload_fileobj(byteBuffer, bucket, generatedURL, ExtraArgs={'ACL': 'public-read'})
        s3Url = "https://" + bucket + ".s3.us-east-2.amazonaws.com/" + generatedURL
        
        return s3Url

    #Takes in a company name and bucket location for upload
    #and uploads the file to S3, and returns the s3 url
    def load_logo(self):
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
        image_filename = self.company.lower() + ".png"
        s3_url_attempt = "https://" + bucket + ".s3.us-east-2.amazonaws.com/" + image_filename
        #Use url to check if already in s3
        is_present = True
        
        s3_resource = boto3.resource('s3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key= AWS_SECRET_KEY)
        try:
            s3_resource.Object(bucket, image_filename).load()
            logger.debug("Image was already saved to s3 %s", s3_url_attempt)
            return s3_url_attempt
        except botocore.exceptions.ClientError as error:
            pass

        logger.debug("Performing clearbit API request to get image %s", self.id)
        #Get company autocomplete and values
        url = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + self.company.lower().split()[0]
        search_result = urllib.request.urlopen(url)
        data = search_result.read()
        encoded_data = search_result.info().get_content_charset('utf-8')
        resulting_data = json.loads(data.decode(encoded_data))
        
        #Create byte buffer representing logo image
        #In the new form of upload, you need to do Image.open(byteBuffer) to access the image itself
        if not resulting_data:
            return None

        item = resulting_data[0]
        clearbit_url = item["logo"]
        logo_response = requests.get(clearbit_url)
        byte_buffer = BytesIO(logo_response.content)
        
        #Upload to S3
        s3.upload_fileobj(byte_buffer, bucket, image_filename, ExtraArgs={'ACL': 'public-read'})
        
        s3Url = "https://" + bucket + ".s3.us-east-2.amazonaws.com/" + image_filename
        logger.debug("Image saved to %s", s3Url)
        
        return s3Url
    
    def __str__(self):
        return '{:39}{:24}{:24}{}\t{:70}'.format(self.title[:35], self.company[:20],
                self.city[:20], self.date_posted, self.url[:70])
