from .scraper import LinkedInScraper
import time
import urllib.request
import os
from profiles.models import Profile, Education, Experience
from constants import *
import logging

logger = logging.getLogger("app")

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

        # Avoid infinite loop
        iteration = 0
        while total_num_profiles_collected < num_profiles and iteration < 3:
            self.scraper.get_profiles(company, title, 
                (num_profiles - total_num_profiles_collected), exclude_usernames)

            profiles = set(Profile.objects.filter(experience__company__icontains=company, 
                                                  experience__title__icontains=title))
            exclude_usernames = [p.username for p in profiles]
            total_num_profiles_collected = len(profiles)

            iteration += 1
            logger.info("Iteration {}, total profiles: {}, looking for {} more"
                .format(iteration, len(profiles), num_profiles - len(profiles)))

        return profiles

    # LinkedIn Search is restricted to certain amount of people,
    # Can use google to search instead.
    def get_linkedin_urls_google_search(self, company, title):
        """
        Using Google Search as another source to fetch profiles.
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        :return: List of urls that were fetched from Google Search API.
        """
        url = "https://www.googleapis.com/customsearch/v1?key=&cx=&q=" + company + title

        search_result = urllib.request.urlopen(url)
        data = search_result.read()
        encoded_data = search_result.info().get_content_charset('utf-8')
        resulting_data = json.loads(data.decode(encoded_data))

        url_list = []

        for results in resulting_data["items"]:
            url_lst.append(results["link"])

        return url_list
