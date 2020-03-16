from profiles.scraper import LinkedInScraper
from profiles.linkedin import LinkedIn
import sys

linkedin_scraper = None
linkedin = None

if any(command in sys.argv for command in ['runserver', 'Seekr.wsgi:application']):
    linkedin_scraper = LinkedInScraper(headless=True)
    linkedin_scraper.login()