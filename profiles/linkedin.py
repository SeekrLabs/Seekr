from .scraper import LinkedInScraper
import time
import urllib.request
import os
import json
#from conf import EMAIL, PASSWORD
from profiles.models import Profile, Education, Experience
from global_variables import linkedin_scraper

class LinkedIn:
    def __init__(self):
        self.scraper = LinkedInScraper()
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
        # first check in the database to see there are enough num_profiles
        # then call get_linkedin_urls_google_search, and then pass those urls to the scraper
        # and then store in the db

        profiles = [p for p in Profile.objects.filter(experience__company__icontains=company, 
                        experience__title__icontains=title)]
        exclude_urls = [p.profile_url for p in profiles]

        total_num_profiles_collected = len(profiles)
        iteration = 0 # NOTE: putting a upper limit to how many times we can search for profiles to avoid infinite loop
        while total_num_profiles_collected < num_profiles and iteration < 3:
            self.scraper.get_profiles(company, title, (num_profiles - total_num_profiles_collected), exclude_urls)
            # NOTE: the missing profiles that we fetched from scraper would be added to the DB by now
            # NOTE: the below query into DB is necessary because we might need to fetch more profiles for the corresponding role
            # NOTE: this can happen when LinkedIn keyword search suggests people working at the company but not under the role we wnat
            profiles = [p for p in Profile.objects.filter(experience__company__icontains=company, 
                        experience__title__icontains=title)] 
            exclude_urls = [p.profile_url for p in profiles]
            total_num_profiles_collected = len(profiles)
            iteration+=1

        return profiles # returning a list of Query objects for now 

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
