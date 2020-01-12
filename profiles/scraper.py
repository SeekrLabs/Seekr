from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import logging
import time
import os
from datetime import date

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
        except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
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

        except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
            if logs:
                logger.warning(f"Couldn't find XPATH: {xpath} ")
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
                    'LINKEDIN_PEOPLE_SEARCH': 'https://www.linkedin.com/search/results/people/?keywords='}
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
        'SHOW_MORE': './/button[@class="pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid"]'
    }

    def login(self):
        self.visit(self.urls['LINKEDIN_LOGIN_URL'])
        time.sleep(2)
        self.get_by_xpath('USERNAME').send_keys(LINKEDIN_EMAIL)
        self.get_by_xpath('PASSWORD').send_keys(LINKEDIN_PASSWORD + '\n')
    
    """
    :param query: String that queries the people tab of linkedin
    """
    def people_search(self, query):
        url = self.urls['LINKEDIN_PEOPLE_SEARCH'] + '%20'.join(query.split())
        self.visit(url)
        self.scroll_to_bottom(2500)
    
    def parse_search_people_result(self):
        els = self.get_multiple_by_xpath_or_none('SEARCH_PEOPLE', wait=True)
        return [LinkedInProfile(el.get_attribute('href'), None, None) for el in els]

    def collect_basic_profile(self, company, role, num_profiles, exclude_urls):
        self.people_search(company, role)
        profiles = []

        while len(profiles) < num_profiles:
            new_profiles = self.parse_search_people_result()
            profiles += [p for p in new_profiles if p.profile_url not in exlucde_urls]

        return profiles

    def get_profiles(self, company, role, num_profiles=20, exlude_urls=[]):
        basic_profiles = self.collect_basic_profile(company, role, num_profiles, exclude_urls)


    def get_profile_by_url(self, profile_url):
        self.visit(profile_url)
        name = self.get_by_xpath_text_or_none('PROFILE_NAME', wait=True)
        location = self.get_by_xpath_text_or_none('LOCATION', wait=False)

        self.scroll_to_bottom(5000)

        experiences = self.parse_profile_experiences()
        education = self.parse_profile_education()
        print(experiences)
        print(education)
        

    def parse_profile_experiences(self):
        experiences = []
        exps = self.get_multiple_by_xpath_or_none('EXPERIENCES')
        if not exps:
            return None
        
        for exp in exps:
            temp = {}
            temp['dates'] = self.element_get_text_by_xpath_or_none(
                    exp, 'DATE_RANGE')
            temp['title'] = self.element_get_text_by_xpath_or_none(
                    exp, 'TITLE')
            temp['company'] = self.element_get_text_by_xpath_or_none(
                    exp, 'COMPANY')
            temp['description'] = self.element_get_text_by_xpath_or_none(
                    exp, 'JOB_DESCRIPTION')
            experiences.append(temp)

        return experiences


    def parse_profile_education(self):
        institution = self.get_by_xpath_text_or_none('SCHOOL', wait=False)
        degree = self.get_by_xpath_text_or_none('DEGREE', wait=False)
        field_of_study = self.get_by_xpath_text_or_none('FIELD_OF_STUDY', wait=False)
        grade = self.get_by_xpath_text_or_none('GRADE', wait=False)
        school_date_range = self.get_by_xpath_text_or_none('SCHOOL_DATE_RANGE', wait=False)
        
        if not institution or not field_of_study or not school_date_range:
            return None  
        degree = degree.split('\n')[1]
        if "bachelor" in degree.lower():
            degree = "Bachelor"
        elif "master" in degree.lower():
            degree = "Master"
        elif "pdh" in degree.lower():
            degree = "PhD"
        else:
            degree = "Other"

        start_date = date(int((school_date_range.split('\n')[1]).split(' ')[0]),9, 1)
        end_date = date(int((school_date_range.split('\n')[1]).split(' ')[2]), 5, 1)

        return {
            "institution": institution,
            "field_of_study": field_of_study.split('\n')[1],
            "degree": degree,
            "grade": grade.split('\n')[1],
            "start_date": start_date,
            "end_date": end_date
        }