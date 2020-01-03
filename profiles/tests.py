from django.test import TestCase
from .models import Profile
from .scraper import LinkedInScraper
import time

class ProfileTestCase(TestCase):
    def setUp(self):
        print("hi")

    def test_false(self):
        linkedin = LinkedInScraper()
        linkedin.login()
        print(linkedin.get_profile_by_url("https://www.linkedin.com/in/waltonwang"))
        linkedin.quit()
        
# Create your tests here.
