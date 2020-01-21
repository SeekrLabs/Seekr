from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException, NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import logging
import time
import os
from datetime import date, datetime
from .models import Profile, Experience, Education
import re

logger = logging.getLogger(__name__)

POLL_FREQUENCY = 0.1
WAIT_TIMEOUT = 20
WINDOW_SIZE = 800
LINKEDIN_EMAIL = os.environ['LINKEDIN_EMAIL']
LINKEDIN_PASSWORD = os.environ['LINKEDIN_PASSWORD']

class SeleniumScraper:
    xpaths = {}
    def __init__(self, headless=False):
        if headless:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            driver = webdriver.Chrome(chrome_options=options)
        else:
            driver = webdriver.Chrome()

        self.d = driver

    def visit(self, url):
        self.d.get(url)

    def quit(self):
        self.d.quit()

    def element_get_by_xpath_or_none(self, el, xpath_key, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None is returned.
        :param driver: Selenium Webdriver to use.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an exception occures.
        :return: The web element or None if nothing found.
        """
        try:
            return el.find_element_by_xpath(self.xpaths[xpath_key])
        except (TimeoutException, StaleElementReferenceException, WebDriverException, NoSuchElementException) as e:
            if logs:
                logger.warning(f"XPATH: {xpath_key} ")
                logger.warning(f"Error: {e} ")
            return None

    def scroll_to_bottom(self, body_height):
        top = 0
        while top < body_height:
            top += WINDOW_SIZE * 2 // 3
            scroll = "window.scrollTo(0, " + str(top) + ")"
            self.d.execute_script(scroll)
            time.sleep(0.1)

    def element_get_text_by_xpath_or_none(self, el, xpath_key, logs=True):
        element = self.element_get_by_xpath_or_none(el, xpath_key, logs)
        if not element:
            return None
        else:
            return element.text

    def wait_get_by_xpath(self, xpath_key):
        """
        Get a web element through the xpath passed by performing a Wait on it.
        :param xpath: xpath to use.
        :return: The web element.
        """
        return WebDriverWait(self.d, WAIT_TIMEOUT, poll_frequency=POLL_FREQUENCY).until(
            ec.presence_of_element_located(
                (By.XPATH, self.xpaths[xpath_key])
            ))

    def get_by_xpath(self, xpath_key):
        """
        Get a web element through the xpath
        :param xpath: xpath to use.
        :return: The web element.
        """
        return self.d.find_element_by_xpath(self.xpaths[xpath_key])

    def get_by_xpath_or_none(self, xpath_key, wait=False, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None is returned.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an exception occures.
        :return: The web element or None if nothing found.
        """
        try:
            if wait:
                return self.wait_get_by_xpath(xpath_key)
            else:
                return self.get_by_xpath(xpath_key)

        except (TimeoutException, StaleElementReferenceException, WebDriverException, NoSuchElementException) as e:
            if logs:
                logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                logger.warning(f"Error: {e} ")
            return None

    def get_by_xpath_text_or_none(self, xpath_key, wait=False, logs=True):
        element = self.get_by_xpath_or_none(xpath_key, wait, logs)
        if not element:
            return None
        else:
            return element.text

    def get_multiple_by_xpath_or_none(self, xpath_key, wait=False, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None is returned.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an exception occures.
        :return: The web element or None if nothing found.
        """
        if wait:
            try:
                # Polling call, returns when something is found
                self.wait_get_by_xpath(xpath_key)
            except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
                if logs:
                    logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                    logger.warning(f"Error: {e} ")
                return None

        try:
            return self.d.find_elements_by_xpath(self.xpaths[xpath_key])
        except:
            if logs:
                if wait:
                    logger.warning(f"Found XPATH: {xpath_key}, couldn't find all elements.")
                    logger.warning(f"Error: {e} ")
                else:
                    logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                    logger.warning(f"Error: {e} ")
            return None

    def get_multiple_by_xpath_text_or_none(self, xpath_key, wait=False, logs=True):
        element = self.get_multiple_by_xpath_or_none(xpath_key, wait, logs)
        if not element:
            return None
        else:
            return [element.text for element in elements]


class LinkedInScraper(SeleniumScraper):
    urls = {'LINKEDIN_LOGIN_URL': 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin',
                    'BASE_LINKEDIN': 'https://www.linkedin.com/',
                    'LINKEDIN_PEOPLE_SEARCH': 'https://www.linkedin.com/search/results/people/?keywords=',
                    'SIGN_IN': 'https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww%2Elinkedin%2Ecom%2Fin%2Fjoyliu3&amp;trk=public_auth-wall_profile'}
    xpaths = {
        'USERNAME': '//*[@id="username"]',
        'PASSWORD': '//*[@id="password"]',
        'SEARCH_PEOPLE': '//*[@data-control-name="search_srp_result"]',
        'SEARCH_RESULT_ITEM': '//li[@class="search-result search-result__occluded-item ember-view"]',
        'PROFILE_NAME': '//*[@class="inline t-24 t-black t-normal break-words"]',
        'LOCATION': '//li[@class="t-16 t-black t-normal inline-block"]',
        'EXPERIENCES': '//*[@class="pv-profile-section__card-item-v2 pv-profile-section pv-position-entity ember-view"]',
        'TITLE': './/h3[@class="t-16 t-black t-bold"]',
        'COMPANY': './/p[@class="pv-entity__secondary-title t-14 t-black t-normal"]',
        'DATE_RANGE': './/h4[@class="pv-entity__date-range t-14 t-black--light t-normal"]',
        'JOB_DESCRIPTION': './/p[@class="pv-entity__description t-14 t-black t-normal inline-show-more-text inline-show-more-text--is-collapsed ember-view"]',
        'SCHOOL': './/h3[@class="pv-entity__school-name t-16 t-black t-bold"]',
        'DEGREE': './/p[@class="pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal"]',
        'FIELD_OF_STUDY': './/p[@class="pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal"]',
        'GRADE': './/p[@class="pv-entity__secondary-title pv-entity__grade t-14 t-black t-normal"]',
        'SCHOOL_DATE_RANGE': './/p[@class="pv-entity__dates t-14 t-black--light t-normal"]',
        'EDUCATION_DESCRIPTION': './/p[@class="pv-entity__description t-14 t-normal mt4"]',
        'SHOW_MORE': './/button[@class="pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid"]'
    }

    last_page_num = 1

    def login(self):
        self.visit(self.urls['LINKEDIN_LOGIN_URL'])
        time.sleep(5)
        self.get_by_xpath('USERNAME').send_keys(LINKEDIN_EMAIL)
        self.get_by_xpath('PASSWORD').send_keys(LINKEDIN_PASSWORD + '\n')

    """
    :param query: String that queries the people tab of linkedin
    """
    def search_profiles_in_company_role(self, company, role):
        url = self.urls['LINKEDIN_PEOPLE_SEARCH'] + company + '&'+'%2f'.join(role.split()) + "&page="+str(self.last_page_num)
        self.last_page_num+=1
        self.visit(url)

    def search_more_profiles(self, company, role, num_profiles_collected): 
        profiles = []
        if (num_profiles_collected) %10 != 0:
            time.sleep(2)
            self.scroll_to_bottom(700)
            profiles = self.d.find_elements_by_xpath('//a[contains(@class, "search-result__result-link ember-view")]')
            self.last_page_num+=1
        else: #when the number of profiles collected is in multiples of 10
            url = self.urls['LINKEDIN_PEOPLE_SEARCH'] + company + '&'+'%2f'.join(role.split()) + "&page="+str(self.last_page_num)
            self.visit(url)
            time.sleep(2)
            profiles = self.d.find_elements_by_xpath('//a[contains(@class, "search-result__result-link ember-view")]')
            
        return profiles

    def collect_basic_profile(self, company, role, num_profiles, exclude_urls):
        self.search_profiles_in_company_role(company, role)
        new_profiles = self.d.find_elements_by_xpath('//a[contains(@class, "search-result__result-link ember-view")]')
        profile_links = set()
        profile_links = set(p.get_attribute('href') for p in new_profiles if p.get_attribute('href') not in exclude_urls)
        
        while len(profile_links) < num_profiles:
            new_profiles = self.search_more_profiles(company, role, len(profile_links))
            for p in new_profiles:
                if p.get_attribute('href') not in exclude_urls:
                    profile_links.add(p.get_attribute('href'))

        return profile_links

    def collect_more_profile(self, num_profiles_collected, num_profiles_needed, company, role):
        profile_links = set()
        num_profiles_collected = num_profiles_collected
        while (num_profiles_collected < num_profiles_needed):
            self.last_page_num+=1
            url = self.urls['LINKEDIN_PEOPLE_SEARCH'] + company + '&'+'%2f'.join(role.split()) + "&page="+str(self.last_page_num)
            self.visit(url)
            time.sleep(2)
            new_profiles = self.d.find_elements_by_xpath('//a[contains(@class, "search-result__result-link ember-view")]')
            profile_links = set()
            profile_links = set(p.get_attribute('href') for p in new_profiles)

            for link in profile_links:
                if self.get_profile_by_url(link) == True:
                    num_profiles_collected +=1

    def store_profiles(self, profile_links):
        num_profiles_saved_to_db = 0
        for link in profile_links:
            if self.get_profile_by_url(link) == True:
                num_profiles_saved_to_db +=1
            time.sleep(2)

        return num_profiles_saved_to_db

    def get_profiles(self, company, role, num_profiles=10, exclude_urls=[]): # get number of profiles as specified in the arg and store them in database
        profiles = self.collect_basic_profile(company, role, num_profiles, exclude_urls)
        num_profiles_saved_to_db = self.store_profiles(profiles)
        self.collect_more_profile(num_profiles_saved_to_db, num_profiles, company, role)

    # returning a boolean to indicate if we have stored the profile into DB 
    def get_profile_by_url(self, profile_url): # storing the profile into the db
        self.visit(profile_url)
        name = self.get_by_xpath_text_or_none('PROFILE_NAME', wait=True)
        location = self.get_by_xpath_text_or_none('LOCATION', wait=False)
        self.scroll_to_bottom(1000)

        experiences = self.parse_profile_experiences()
        education = self.parse_profile_education()

        if experiences is None or education is None: # not a valid profile to be stored in DB
            return False 

        gpa = None
        if education['grade'] is not None:
            gpa = LinkedInScraper.extract_gpa(education['grade'])

        is_education_current = False
        if education["end_date"] >= datetime.today():
            is_education_current = True

        # parsing the start and end date for experiences
        experience_date_range = experiences[0]["dates"]
        is_experience_current = True
        experience_start_date_month = experience_date_range.split('\n')[1].split(' ')[0]
        experience_start_date_year = experience_date_range.split('\n')[1].split(' ')[1]
        experience_start_date = datetime.strptime(experience_start_date_month + " 01 " + experience_start_date_year, '%b %d %Y')
        experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[3]
        experience_end_date = datetime.now().strftime("%Y-%m-%d")

        if experience_end_date_month != "Present":
            is_experience_current = False
            experience_end_date_year = experience_date_range.split('\n')[1].split(' ')[4]
            experience_end_date = datetime.strptime(experience_end_date_month + " 01 " + experience_end_date_year, '%b %d %Y')

        # constructing the Profile object first by setting the name and location
        profile = Profile(name = name, location = location, profile_url = profile_url)
        profile.save()
        profile.experience_set.create(
                company=experiences[0]["company"],
                description=experiences[0]["description"],
                title = experiences[0]["title"],
                start_date=experience_start_date,
                end_date=experience_end_date,
                is_current=is_experience_current
        )

        profile.education_set.create(
                school_name=education['institution'],
                degree=education['degree'],
                field_of_study = education['field_of_study'],
                description=education['description'],
                gpa=gpa,
                start_date=education["start_date"],
                end_date=education["end_date"],
                is_current=is_education_current
        )

        # saving the entire profile into DB
        profile.save()
        return True

    def parse_profile_experiences(self):
        experiences = []
        exps = self.get_multiple_by_xpath_or_none('EXPERIENCES')
        if not exps:
            return None

        for exp in exps:
            temp = {}
            temp['dates'] = self.element_get_text_by_xpath_or_none(
                    exp, 'DATE_RANGE') if self.element_get_text_by_xpath_or_none(exp, 'DATE_RANGE') is not None else ""
            temp['title'] = self.element_get_text_by_xpath_or_none(
                    exp, 'TITLE') if self.element_get_text_by_xpath_or_none(exp, 'TITLE') is not None else ""
            temp['company'] = self.element_get_text_by_xpath_or_none(
                    exp, 'COMPANY') if self.element_get_text_by_xpath_or_none(exp, 'COMPANY') is not None else ""
            temp['description'] = self.element_get_text_by_xpath_or_none(
                    exp, 'JOB_DESCRIPTION') if self.element_get_text_by_xpath_or_none(exp, 'JOB_DESCRIPTION') is not None else ""
            experiences.append(temp)

        return experiences

    def extract_gpa(grade):
        gpas = re.findall('[0-4]\.[0-9]?[0-9]?', grade)
        if not gpas:
            return None

        gpas = map(lambda x: float(x), gpas)
        return min(gpas)

    def parse_profile_education(self):
        institution = self.get_by_xpath_text_or_none('SCHOOL', wait=False) if self.get_by_xpath_text_or_none('SCHOOL', wait=False) is not None else ""
        degree = self.get_by_xpath_text_or_none('DEGREE', wait=False) if self.get_by_xpath_text_or_none('DEGREE', wait=False) is not None else ""
        field_of_study = self.get_by_xpath_text_or_none('FIELD_OF_STUDY', wait=False) if self.get_by_xpath_text_or_none('FIELD_OF_STUDY', wait=False) is not None else ""
        grade = self.get_by_xpath_text_or_none('GRADE', wait=False).split('\n')[1] if self.get_by_xpath_text_or_none('GRADE', wait=False) is not None else ""
        school_date_range = self.get_by_xpath_text_or_none('SCHOOL_DATE_RANGE', wait=False) if self.get_by_xpath_text_or_none('SCHOOL_DATE_RANGE', wait=False) is not None else ""
        description = "" # blank for now

        if not institution or not field_of_study or not school_date_range:
            return None
        
        degree = degree.split('\n')[1]
        if "bachelor" in degree.lower():
            degree = "Bachelor"
        elif "master" in degree.lower():
            degree = "Master"
        elif "phd" in degree.lower():
            degree = "PhD"
        else:
            degree = "Other"

        start_date = datetime(int(school_date_range.split('\n')[1].split(' ')[0]), 9, 1)
        end_date = datetime(int(school_date_range.split('\n')[1].split(' ')[2]), 5, 1)

        return {
            "institution": institution,
            "field_of_study": field_of_study.split('\n')[1],
            "degree": degree,
            "grade": grade,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        }