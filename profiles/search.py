import requests
import os
import json
import logging
from .models import Profile

logger = logging.getLogger('app')

class GoogleSearch:
    def construct_api_url(**kwargs):
        base_url = "https://www.googleapis.com/customsearch/v1?" \
            + "key=" + os.environ['GOOGLE_SEACH_KEY'] \
            + "&cx=" + os.environ['GOOGLE_SE_ID']
        
        for key, val in kwargs.items():
            base_url += "&" + key + "=" + val
        logger.info("Constructed url {}".format(base_url))
        return base_url

    # 1. Can get pictures from the response
    # 2. LinkedIn search engine must match domain.
    def get_linkedin_profiles_simple(query, page_num=0):
        url = GoogleSearch.construct_api_url(q=query, start=str(page_num * 10 + 1) )
        
        response = requests.get(url)
        response_json = response.json()

        profiles = []

        for result in response_json['items']:
            profiles.append({
                "profile_url": result['link'],
                "picture_url": result['pagemap']['cse_image'][0]['src']})


        usernames = " ".join([Profile.url_to_username(p['profile_url']) for p in profiles])
        logger.info("Found the following profiles {}.".format(usernames))
        
        return profiles

    def get_linkedin_profiles(query, num_pages, start_page=0):
        profiles = []
        for i in range(start_page, start_page + num_pages):
            profiles += GoogleSearch.get_linkedin_profiles_simple(query, page_num=i)
        return profiles