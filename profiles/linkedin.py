from .scraper import LinkedInScraper
import time
import urllib.request
import os
from profiles.models import Profile, Education, Experience
from constants import *
import logging

logger = logging.getLogger('app')

class LinkedIn:
    def __init__(self, linkedin_scraper):
        self.scraper = linkedin_scraper
        self.scraper.login()

    # Checks database for matches, and scrapes more if not enough
    def get_profiles(self, company, title, num_profiles):
        """
        Get profiles based on the company, title.
        This calls the get_profiles in scraper.py
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        :param num_profiles: Required number of profiles to fetch and store.
        :return: List of Query objects of the profiles stored in the Profiles database that corresponds to the company and title.
        """

        # Checks DB first and then scrapes from linkedin
        logger.info("Looking for profiles that's worked at {} as {}".format(company, title))
        profiles = set(Profile.objects.filter(experience__company__icontains=company, 
                                              experience__title__icontains=title))

        exclude_usernames = [p.username for p in profiles]
        logger.info("Found {} existing profiles in database, looking for {} more."
            .format(len(profiles), max(0, num_profiles - len(profiles))))

        total_num_profiles_collected = len(profiles)
        self.scraper.get_profiles(company, title, 
            (num_profiles - total_num_profiles_collected), exclude_usernames)

        profiles = Profile.objects.filter(experience__company__icontains=company, 
                                              experience__title__icontains=title)
        logger.info("Found a total of {} profiles".format(len(profiles)))
        return profiles