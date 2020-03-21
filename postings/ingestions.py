import time
from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import datetime
from .models import Posting
import sys
import logging
from constants import CANADA_LOCATIONS, US_LOCATIONS, TITLES
from profiles.scraper import LinkedInScraper
from profiles.linkedin import LinkedIn

logger = logging.getLogger('app')

def repeat():
    indeed = IndeedIngestion(ca_locations=CANADA_LOCATIONS,
        us_locations=US_LOCATIONS,
        titles=TITLES)
    
    while True:
        seconds_til_midnight = time_until_end_of_day().seconds
        logger.info("Sleeping for %d seconds." % seconds_til_midnight)
        time.sleep(seconds_til_midnight)
        logger.info('Starting Indeed ingestion.')
        indeed.ingest_jobs(1)
        

def time_until_end_of_day(dt=None):
    """
    Get timedelta until end of day on the datetime passed, or current time.
    """
    if dt is None:
        dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    return datetime.datetime.combine(tomorrow, datetime.time.min) - dt

class IndeedIngestion:
    BASE_URL_CA = 'https://www.indeed.ca/jobs?&sort=date&limit=50'
    BASE_URL_US = 'https://www.indeed.com/jobs?&sort=date&limit=50'

    def __init__(self, ca_locations, us_locations, titles):
        self.ca_locations = ca_locations
        self.us_locations = us_locations
        self.titles = titles

    def ingest_jobs(self, num_prev_days):
        linkedin_scraper = LinkedInScraper(headless=True)
        self.linkedin = LinkedIn(linkedin_scraper)
        for ca_loc in self.ca_locations:
            for title in self.titles:
                url = self.BASE_URL_CA + '&q=' + title + '&l=' + ca_loc
                self.ingest_jobs_from_url(url, num_prev_days, title, 'canada')

        for us_loc in self.us_locations:
            for title in self.titles:
                url = self.BASE_URL_US + '&q=' + title + '&l=' + us_loc
                self.ingest_jobs_from_url(url, num_prev_days, title, 'usa')
        linkedin_scraper.quit()

    def ingest_jobs_from_url(self, start_url, num_prev_days, search_title, country):
        page_num = 0

        backfill_date = date.today() - timedelta(days=num_prev_days)
        posting_in_range = True

        while posting_in_range:
            url = start_url + '&start=' + str(page_num * 50)
            page_num += 1

            logger.info('Issuing GET: ' + url)
            search_result = requests.get(url)

            if search_result.status_code != 200:
                logger.error("GET Failed, Status Code {}".format(search_result.status_code))
                continue

            logger.info('GET Success, Parsing...')
            search_soup = BeautifulSoup(search_result.text, 'html.parser')

            logger.info('Finding individual job postings...')
            posting_soups = search_soup.find_all('div', {'class': 'jobsearch-SerpJobCard'})
            logger.info('Found ' + str(len(posting_soups)) + ' ad cards.')

            postings = []
            for posting_soup in posting_soups:
                posting = IndeedJobAd(posting_soup, country, search_title)
                if posting.valid:
                    posting.print()
                    posting_db = posting.to_model()
                    postings.append(posting_db)
            
            existing_postings = Posting.objects.filter(pk__in=[p.id for p in postings])
            num_existing_postings = len(existing_postings)
            logger.info("Length of existing postings: {}".format(num_existing_postings))

            existing_postings_id = [p.id for p in existing_postings]

            if num_existing_postings > 40:
                posting_in_range = False
            
            filtered_postings = []
            for p in postings:
                if p.id not in existing_postings_id:
                    logger.info("Generating posting vector...")
                    p.generate_vector(5, self.linkedin)
                    try:
                        logger.info("Saving posting {}".format(p.id))
                        p.save()
                    except:
                        logger.exception("Error")

            if page_num == 20:
                posting_in_range = False
                
            if not posting_in_range:
                logger.info("Stopping Ingestion.")

            # Server can't handle load.
            break
                

class IndeedJobAd:
    # Constants
    BASE_INDEED = 'https://www.indeed.com'
    SOUP_ID = {
        'TITLE_URL': {'el': 'a',
                    'tag': 'class', 
                    'attr': 'jobtitle'},
        'COMPANY': {'el': 'span', 
                  'tag': 'class', 
                  'attr': 'company'},
        'DATE_POSTED': {'el': 'span', 
                      'tag': 'class', 
                      'attr': 'date'},
        'DESCRIPTION': {'el': 'div', 
                      'tag': 'class', 
                      'attr': 'summary'},
        'LOCATION': {'el': 'span', 
                   'tag': 'class', 
                   'attr': 'location'}
    }

    # Initalize with a BeautifulSoup Card element
    def __init__(self, ad_soup, country, search_title):
        self.country = country
        self.valid = self.extract_card(ad_soup)
        self.search_title = search_title
        if self.valid:
            self.id = (self.title+'-'+self.company+'-' \
                    +self.city+'-'+str(self.date_posted)
            ).lower().replace(' ', '_')

    def print(self):
        if self.valid:
            location = self.city + ', ' + self.state + ' ' + self.country
            logger.info('{:39}{:24}{:24}{} {:70}'.format(self.title[:35], self.company[:20],
                    location, self.date_posted, self.url[:70]))
        else:
            logger.warning("Invalid")

    def to_model(self):
        if self.valid:
            return Posting(id=self.id, title=self.title, company=self.company, 
                    city=self.city, state=self.state, country=self.country,
                    source=self.source, date_posted=self.date_posted,
                    url=self.url, description=self.description, 
                    search_title=self.search_title)
        else:
            return None

    # Returns false if Job Posting is sponsored
    def extract_card(self, ad_soup):
        title_soup = self.find_element_from_soup(ad_soup, 'TITLE_URL')
        
        if title_soup and 'pagead' not in title_soup['href']:
            url = title_soup['href']
            company_soup = self.find_element_from_soup(ad_soup, 'COMPANY')
            date_posted_soup = self.find_element_from_soup(ad_soup, 'DATE_POSTED')
            description_soup = self.find_element_from_soup(ad_soup, 'DESCRIPTION')
            location_soup = self.find_element_from_soup(ad_soup, 'LOCATION')

            if title_soup and company_soup and date_posted_soup and location_soup:

                self.title = title_soup.text.strip()
                self.url = self.BASE_INDEED + title_soup['href']
                self.source = 'indeed'
                self.company = company_soup.text.strip()
                self.date_posted = self.get_post_date(date_posted_soup.text.strip())
                self.description = description_soup.text
                self.location = location_soup.text.strip()
                self.city = self.location.split(',')[0]
                try:
                    self.state = self.location.split(',')[1].split()[0]
                except:
                    logger.warning('no state ' + self.location + ' ' + self.url + '\n\n\n\n\n\n')
                    return False
                return True
            
            else:
                logger.warning('Could not find enough information {}'.format(url))

        return False

    def visit_link_to_extract_description(self):
        if self.url:
            job_url = self.url

            logger.info('Issuing GET: ' + job_url)
            job_response = requests.get(job_url)
            logger.info('GET Success, Parsing...')

            specific_job_soup = BeautifulSoup(job_response.text, 'html.parser')
            description = self.find_element_from_soup(specific_job_soup,
                    {'el': 'div',
                      'tag': 'class',
                      'attr': 'jobsearch-JobComponent-description'})
            if description:
                self.description = str(description)

    def get_post_date(self, delta_post_date):
        today = date.today()

        if 'day' in delta_post_date and delta_post_date != 'Today':
            delta_days = int(delta_post_date[0:2].strip())
            return today - timedelta(days=delta_days)
        else:
            return today

    def find_element_from_soup(self, soup, spec_name):
        spec = self.SOUP_ID[spec_name]
        result = soup.find(spec['el'], {spec['tag'], spec['attr']})
        if not result:
            logger.warning("Could not find {}".format(spec_name))
        return result