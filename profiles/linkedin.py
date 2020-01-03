from .scraper import LinkedInScraper
import time
from conf import EMAIL, PASSWORD

class LinkedIn:
    def __init__(self):
        self.scraper = LinkedInScraper()

    

    # Checks database for matches, and scrapes more if not enough
    def get_profiles(self, company, title, num_profiles):
        pass

    # LinkedIn Search is restricted to certain amount of people,
    # Can use google to search instead.
    def get_linkedin_urls_google_search(self, company, title):
        pass