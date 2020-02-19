from profiles.scraper import LinkedInScraper
import sys

# Need selenium installation
linkedin_scraper = None

# if any(command in sys.argv for command in ['runserver']):
#     linkedin_scraper = LinkedInScraper()
#     linkedin_scraper.login()

# else:
#     linkedin_scraper = None