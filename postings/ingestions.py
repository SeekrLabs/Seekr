import time
from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import datetime
from .models import Posting

def repeat():
    indeed = IndeedIngestion()
    while True:
        seconds_til_midnight = time_until_end_of_day().seconds
        print("Sleeping for %d seconds." % seconds_til_midnight)
        time.sleep(seconds_til_midnight)
        print('Starting Indeed ingestion.')
        indeed.ingest_jobs()
        

def time_until_end_of_day(dt=None):
    """
    Get timedelta until end of day on the datetime passed, or current time.
    """
    if dt is None:
        dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    return datetime.datetime.combine(tomorrow, datetime.time.min) - dt

class IndeedIngestion():
    canada_locations = ['toronto']
    titles = ['engineer']
    BASE_URL_CA = 'https://www.indeed.ca/jobs?&sort=date&limit=50'
    
    def ingest_jobs(self):
        for ca_loc in self.canada_locations:
            for title in self.titles:
                url = self.BASE_URL_CA + '&q=' + title + '&l=' + ca_loc
                self.ingest_jobs_from_url(url, ca_loc)

    def ingest_jobs_from_url(self, start_url, location):
        today = date.today()
        postings = []
        ad_num = 0
        posted_in_last_day = True
        while posted_in_last_day:
            url = start_url + '&start=' + str(ad_num)
            ad_num += 50
            print('Issuing GET: ' + url)
            search_result = requests.get(url)

            print('GET Success, Parsing...')
            search_soup = BeautifulSoup(search_result.text, 'html.parser')

            print('Finding individual job postings...')
            posting_soups = search_soup.find_all('div', {'class': 'jobsearch-SerpJobCard'})
            print('Found ' + str(len(posting_soups)) + ' ad cards.')

            for posting_soup in posting_soups:
                posting = IndeedJobAd(posting_soup, location)
                if posting.valid:
                    posting.print()
                    posting_db = posting.to_model()
                    posting_db.save()

                    posted_in_last_day = (posting.date_posted == today) \
                            or (posting.date_posted == today - timedelta(days=1))
                    if not posted_in_last_day:
                        print("Stopping Ingestion.")

class IndeedJobAd:
    # Constants
    BASE_INDEED = 'https://www.indeed.com'
    title_url_soup_id = [{'el': 'a', 
                         'tag': 'class', 
                         'attr': 'jobtitle'}]
    company_soup_id = [{'el': 'span', 
                       'tag': 'class', 
                       'attr': 'company'}]
    date_posted_soup_id = [{'el': 'span', 
                           'tag': 'class', 
                           'attr': 'date'}]
    description_soup_id = [{'el': 'div', 
                    'tag': 'class', 
                    'attr': 'summary'}]

    # Initalize with a BeautifulSoup Card element
    def __init__(self, ad_soup, location):
        self.title = None
        self.company = None
        self.location = location
        self.source = None
        self.date_posted = None
        self.url = None
        self.description = None
        self.valid = self.extract_card(ad_soup)
        if self.valid:
            self.id = (self.title+'-'+self.company+'-' \
                    +self.location+'-'+str(self.date_posted)
            ).lower().replace(' ', '_')

    def print(self):
        if self.valid:
            print("title: ", self.title)
            print("company: ", self.company)
            print("location: ", self.location)
            print("source: ", self.source)
            print("date_posted: ", self.date_posted)
            print("url: ", self.url)
            print("description: ", self.description)
            print()
        else:
            print("Invalid\n")

    def to_model(self):
        if self.valid:
            return Posting(id=self.id, title=self.title, company=self.company, 
                    location=self.location, source=self.source, date_posted=self.date_posted,
                    url=self.url, description=self.description)
        else:
            return None

    # Returns false if Job Posting is sponsored
    def extract_card(self, ad_soup):
        title_soup = find_element_from_soup(ad_soup, self.title_url_soup_id)
        company_soup = find_element_from_soup(ad_soup, self.company_soup_id)
        date_posted_soup = find_element_from_soup(ad_soup, self.date_posted_soup_id)
        description_soup = find_element_from_soup(ad_soup, self.description_soup_id)
    

        if title_soup and company_soup and date_posted_soup \
                and 'pagead' not in title_soup['href']:
            self.title = title_soup.text.strip()
            self.url = self.BASE_INDEED + title_soup['href']
            self.source = 'indeed'
            self.company = company_soup.text.strip()
            self.date_posted = self.get_post_date(date_posted_soup.text.strip())
            self.description = description_soup.text
            return True

        else:
            return False

    def visit_link_to_extract_description(self):
        if self.url:
            job_url = self.url

            print('Issuing GET: ' + job_url)
            job_response = requests.get(job_url)
            print('GET Success, Parsing...')

            specific_job_soup = BeautifulSoup(job_response.text, 'html.parser')
            description = find_element_from_soup(specific_job_soup,
                    [{'el': 'div',
                      'tag': 'class',
                      'attr': 'jobsearch-JobComponent-description'}])
            if description:
                self.description = str(description)

    def get_post_date(self, delta_post_date):
        today = date.today()

        if 'day' in delta_post_date and delta_post_date != 'Today':
            delta_days = int(delta_post_date[0:2].strip())
            return today - timedelta(days=delta_days)
        else:
            return today


def find_element_from_soup(soup, specs):
    for spec in specs:
        # print('Looking for ' + spec['el'] + ' ' + spec['tag']
        #         + ' ' + spec['attr'] + '... Found if not otherwise stated.')
        result = soup.find(spec['el'], {spec['tag'], spec['attr']})
        if result:
            return result
    print('NOT FOUND ' + specs[0]['attr'] + '... '  + str(soup.attrs))
    return None