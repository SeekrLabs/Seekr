import time
from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import datetime
from .models import Posting
import sys

def repeat():
    indeed = IndeedIngestion(ca_locations=['toronto', 'vancouver', 'montreal'],
            us_locations=['new york', 'seattle', 'san francisco', 'chicago'],
            titles = ['software', 'hardware', 'analyst'])
    num_init_pages = int(sys.argv[-1])
    indeed.ingest_jobs(num_init_pages)
    
    while True:
        seconds_til_midnight = time_until_end_of_day().seconds
        print("Sleeping for %d seconds." % seconds_til_midnight)
        time.sleep(seconds_til_midnight)
        print('Starting Indeed ingestion.')
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
    # ca_locations = ['toronto']
    # titles = ['engineer', ]
    BASE_URL_CA = 'https://www.indeed.ca/jobs?&sort=date&limit=50'
    BASE_URL_US = 'https://www.indeed.com/jobs?&sort=date&limit=50'

    def __init__(self, ca_locations, us_locations, titles):
        self.ca_locations = ca_locations
        self.us_locations = us_locations
        self.titles = titles

    def ingest_jobs(self, num_prev_days):
        for ca_loc in self.ca_locations:
            for title in self.titles:
                url = self.BASE_URL_CA + '&q=' + title + '&l=' + ca_loc
                self.ingest_jobs_from_url(url, num_prev_days, 'canada')

        for us_loc in self.us_locations:
            for title in self.titles:
                url = self.BASE_URL_US + '&q=' + title + '&l=' + us_loc
                self.ingest_jobs_from_url(url, num_prev_days, 'usa')

    def ingest_jobs_from_url(self, start_url, num_prev_days, country):
        
        page_num = 0

        backfill_date = date.today() - timedelta(days=num_prev_days)
        posting_in_range = True

        while posting_in_range:
            url = start_url + '&start=' + str(page_num * 50)
            page_num += 1

            print('Issuing GET: ' + url)
            search_result = requests.get(url)

            if search_result.status_code != 200:
                print("GET Failed, Status Code {}".format(search_result.status_code))
                continue

            print('GET Success, Parsing...')
            search_soup = BeautifulSoup(search_result.text, 'html.parser')

            print('Finding individual job postings...')
            posting_soups = search_soup.find_all('div', {'class': 'jobsearch-SerpJobCard'})
            print('Found ' + str(len(posting_soups)) + ' ad cards.')

            postings = []
            for posting_soup in posting_soups:
                posting = IndeedJobAd(posting_soup, country)
                if posting.valid:
                    posting.print()
                    posting_db = posting.to_model()
                    postings.append(posting_db)
                    posting_in_range = (posting.date_posted >=  backfill_date)
            
            existing_postings = Posting.objects.filter(pk__in=[p.id for p in postings])
            num_existing_postings = len(existing_postings)
            print("Length of existing postings: {}".format(num_existing_postings))

            existing_postings_id = [p.id for p in existing_postings]

            if num_existing_postings > 20:
                posting_in_range = False
            
            postings = []
            for p in postings:
                if p.id not in existing_postings_id:
                    if p.generate_vector(10):
                        postings.append(p)
                    

            print("Length of about to be commited postings: {}".format(len(postings)))
            Posting.objects.bulk_create(postings)

            if page_num == 19:
                posting_in_range = False
                
            if not posting_in_range:
                print("Stopping Ingestion.")
                

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
    def __init__(self, ad_soup, country):
        self.country = country
        self.valid = self.extract_card(ad_soup)
        if self.valid:
            self.id = (self.title+'-'+self.company+'-' \
                    +self.city+'-'+str(self.date_posted)
            ).lower().replace(' ', '_')

    def print(self):
        if self.valid:
            location = self.city + ', ' + self.state + ' ' + self.country
            print('{:39}{:24}{:24}{} {:70}'.format(self.title[:35], self.company[:20],
                    location, self.date_posted, self.url[:70]))
        else:
            print("Invalid")

    def to_model(self):
        if self.valid:
            return Posting(id=self.id, title=self.title, company=self.company, 
                    city=self.city, state=self.state, country=self.country,
                    source=self.source, date_posted=self.date_posted,
                    url=self.url, description=self.description)
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
                    print('no state ' + self.location + ' ' + self.url + '\n\n\n\n\n\n')
                    return False
                return True
            
            else:
                print(url)

        return False

    def visit_link_to_extract_description(self):
        if self.url:
            job_url = self.url

            print('Issuing GET: ' + job_url)
            job_response = requests.get(job_url)
            print('GET Success, Parsing...')

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
            print("Could not find {}".format(spec_name))
        return result