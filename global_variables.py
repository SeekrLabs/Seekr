from profiles.scraper import LinkedInScraper
from profiles.linkedin import LinkedIn
import sys

# Need selenium installation
linkedin_scraper = None
linkedin = None

# if any(command in sys.argv for command in ['runserver']):
#     linkedin_scraper = LinkedInScraper()
#     linkedin_scraper.login()

# else:
#     linkedin_scraper = None