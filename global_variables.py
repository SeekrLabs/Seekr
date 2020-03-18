from profiles.scraper import LinkedInScraper
from profiles.linkedin import LinkedIn
import sys

linkedin_scraper = None
linkedin = None

if any(command in sys.argv for command in ['runserver', 'Seekr.wsgi:application', 'ingest']):
    linkedin_scraper = LinkedInScraper(headless=True)
    linkedin = LinkedIn(linkedin_scraper)