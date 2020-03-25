from profiles.scraper import LinkedInScraper
from profiles.linkedin import LinkedIn
import sys
import boto3
from constants import AWS_ACCESS_KEY, AWS_SECRET_KEY

linkedin_scraper = None
linkedin = None

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

if any(command in sys.argv for command in ['runserver', 'Seekr.wsgi:application', 'ingest']):
    linkedin_scraper = LinkedInScraper(headless=True)
    linkedin = LinkedIn(linkedin_scraper)