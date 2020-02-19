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
                return None
                #logger.warning(f"XPATH: {xpath_key} ")
                #logger.warning(f"Error: {e} ")
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
        :param xpath_key: xpath_key to use to access the xpath dictionary
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
                return None
                #logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                #logger.warning(f"Error: {e} ")
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
                    return None
                    #logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                    #logger.warning(f"Error: {e} ")
                return None

        try:
            return self.d.find_elements_by_xpath(self.xpaths[xpath_key])
        except:
            if logs:
                if wait:
                    return None
                    #logger.warning(f"Found XPATH: {xpath_key}, couldn't find all elements.")
                    #logger.warning(f"Error: {e} ")
                else:
                    return None
                    #logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                    #logger.warning(f"Error: {e} ")
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
        'COMPANY_SEQUENTIAL': './/h3[@class="t-16 t-black t-bold"]',
        'DATE_RANGE': './/h4[@class="pv-entity__date-range t-14 t-black--light t-normal"]',
        'JOB_DESCRIPTION': './/p[@class="pv-entity__description t-14 t-black t-normal inline-show-more-text inline-show-more-text--is-collapsed ember-view"]',
        'EDUCATION_MULTIPLE': '//*[@class="pv-profile-section__sortable-card-item pv-education-entity pv-profile-section__card-item ember-view"]',
        'EDUCATION_SINGLE': '//li[@class="pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view"]',
        'SCHOOL': './/h3[@class="pv-entity__school-name t-16 t-black t-bold"]',
        'DEGREE': './/p[@class="pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal"]',
        'FIELD_OF_STUDY': './/p[@class="pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal"]',
        'GRADE': './/p[@class="pv-entity__secondary-title pv-entity__grade t-14 t-black t-normal"]',
        'SCHOOL_DATE_RANGE': './/p[@class="pv-entity__dates t-14 t-black--light t-normal"]',
        'EDUCATION_DESCRIPTION': './/p[@class="pv-entity__description t-14 t-normal mt4"]',
        'SHOW_MORE': './/button[@class="pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid"]',
        'FETCH_PROFILE_FROM_SEARCH': '//a[contains(@class, "search-result__result-link ember-view")]'
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
        """
        Helper function that simply visits the search site for list of profiles.
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        """
        url = self.urls['LINKEDIN_PEOPLE_SEARCH'] + company + '&'+'%2f'.join(role.split()) + "&page="+str(self.last_page_num)
        self.visit(url)

    def search_more_profiles(self, company, role, num_profiles_collected): 
        """
        Helper functon that helps to go to the next search page and search through the whole page for profiles.
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        :param num_profiles_collected: Required to determine if we should continue to search on the same page or go to next search page.
        :return: list of profiles as web elements
        """
        profiles = []
        if (num_profiles_collected) %10 != 0:
            time.sleep(2)
            self.scroll_to_bottom(800)
            profiles = self.get_multiple_by_xpath_or_none('FETCH_PROFILE_FROM_SEARCH')
            self.last_page_num+=1
        else: # NOTE: when the number of profiles collected is in multiples of 10
            url = self.urls['LINKEDIN_PEOPLE_SEARCH'] + company + '&'+'%2f'.join(role.split()) + "&page="+str(self.last_page_num)
            self.visit(url)
            time.sleep(2)
            profiles = self.get_multiple_by_xpath_or_none('FETCH_PROFILE_FROM_SEARCH')     
        return profiles

    def collect_basic_profile(self, company, role, num_profiles, exclude_urls):
        """
        Helper function that gets all the profile links from the returned web elements from search_more_profiles
        :param company: Company name we're searching.
        :param role: Role we're searching for, necessary for helper function to visit the site as role is a keyword.
        :param num_profiles: Required number of profiles to fetch and store.
        :return: list of profile links that were scraped from the search page.
        """
        self.search_profiles_in_company_role(company, role)
        new_profiles = self.get_multiple_by_xpath_or_none('FETCH_PROFILE_FROM_SEARCH')  
        profile_links = set()
        profile_links = set(p.get_attribute('href') for p in new_profiles if p.get_attribute('href') not in exclude_urls)
        
        new_profiles = self.search_more_profiles(company, role, len(profile_links))
        for p in new_profiles:
            if p.get_attribute('href') not in exclude_urls:
                profile_links.add(p.get_attribute('href'))

        # profile_links will always contain the entire set of profiles you see on a search page
        return profile_links

    def store_profiles(self, profile_links, company, role, num_profiles_needed):
        """
        Stores the profiles from profile_links into the Profiles Database.
        We are storing all profiles that have worked at the desired company but might not be working under the desired role.
        :param profile_links: Fetched links from previous helper functions.
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        :param num_profiles: Required number of profiles to fetch and store.
        :return: number of profiles that were saved to db and for each of these profiles, their profile link will be added to exclude_urls which will be returned.
        """
        num_profiles_saved_to_db = 0
        exclude_urls = []
        for link in profile_links:
            if self.get_profile_by_url(link, company, role) == True and num_profiles_saved_to_db<num_profiles_needed:
                num_profiles_saved_to_db +=1
                exclude_urls.append(link)
            elif num_profiles_saved_to_db>=num_profiles_needed:
                return num_profiles_saved_to_db, exclude_urls

            time.sleep(2)

        return num_profiles_saved_to_db, exclude_urls

    def get_profiles(self, company, role, num_profiles, exclude_urls=[]): 
        """
        Get the required number of profiles.
        This is done by multiple helper functions above.
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        :param num_profiles: Required number of profiles to fetch and store.
        :param exclude_urls: List of profile to exclude from fetching.
        """
        profiles = self.collect_basic_profile(company, role, num_profiles, exclude_urls)
        num_profiles_saved_to_db, new_exclude_urls = self.store_profiles(profiles, company, role, num_profiles)
        exclude_urls += new_exclude_urls

        iteration = 0 # NOTE: putting a limit to avoid infinite while loop

        while num_profiles_saved_to_db < num_profiles and iteration < 5:
            num_profiles_needed = num_profiles-num_profiles_saved_to_db
            profile_links = self.collect_basic_profile(company, role, num_profiles_needed, exclude_urls)
            num_new_profiles_saved_to_db, new_exclude_urls = self.store_profiles(profile_links, company, role, num_profiles_needed)
            exclude_urls += new_exclude_urls
            num_profiles_saved_to_db += num_new_profiles_saved_to_db
            iteration+=1

    def get_profile_by_url(self, profile_url, company, role): 
        """
        Scrape basic information of a profile through the given profile URL and store them in Profiles DB.
        This is done by login into LinkedIn and going to the given profile URL.
        If the profile doesn't have experience or education fields we need, then do not store into DB.
        :param profile_url: Person's profile URL that we will be extracting information from.
        :return: True if we have stored the profile into DB, False if we did not store.
        """
        
        self.visit(profile_url)
        name = self.get_by_xpath_text_or_none('PROFILE_NAME', wait=True)
        location = self.get_by_xpath_text_or_none('LOCATION', wait=False)
        self.scroll_to_bottom(1200)

        experiences = self.parse_profile_experiences(company, role)
        if experiences is None: # saving time so we don't need to scrape education
            return False

        educations = self.parse_profile_education()

        if educations is None: # not a valid profile to be stored in DB
            return False 

        gpa = None
        profile = Profile(name = name, location = location, profile_url = profile_url)
        profile.save()
        for education in educations:
            if education['grade'] is not None:
                gpa = LinkedInScraper.extract_gpa(education['grade'])
            
            is_education_current = False
            if education["end_date"] >= datetime.today():
                is_education_current = True

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
            profile.save()         

        for experience in experiences:
            is_experience_current = True
            # NOTE: LinkedIn requires users to input experience date range
            experience_date_range = experience["dates"]
            experience_start_date = datetime.now().strftime("%Y-%m-%d")
            experience_end_date = datetime.now().strftime("%Y-%m-%d")

            experience_start_date_month = experience_date_range.split('\n')[1].split(' ')[0]
                
            if str.isdigit(experience_start_date_month): # NOTE: if user decides to not put a month for start date
                experience_start_date_year = experience_start_date_month
                experience_start_date = datetime.strptime("Jan" + " 01 " + experience_start_date_year, '%b %d %Y')
            else:
                experience_start_date_year = experience_date_range.split('\n')[1].split(' ')[1]
                experience_start_date = datetime.strptime(experience_start_date_month + " 01 " + experience_start_date_year, '%b %d %Y')

            try: 
                experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[2]
            except IndexError: # NOTE: when user only put year for both start and end date
                experience_end_date = datetime.strptime("Dec" + " 01 " + experience_start_date_year, '%b %d %Y')
            else:
                try:
                    experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[3]
                except IndexError: # NOTE: this means that user either put present or just put a year for end date
                    experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[2]
                else: 
                    experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[3]

                if experience_end_date_month != "Present":
                    is_experience_current = False
                    if str.isdigit(experience_end_date_month): # NOTE: if user decides to not put a month for end date
                        experience_end_date_year = experience_end_date_month
                        experience_end_date = datetime.strptime("Dec" + " 01 " + experience_end_date_year, '%b %d %Y')

                    else:
                        experience_end_date_year = experience_date_range.split('\n')[1].split(' ')[4]
                        experience_end_date = datetime.strptime(experience_end_date_month + " 01 " + experience_end_date_year, '%b %d %Y')
        
            profile.experience_set.create(
                    company=experience["company"],
                    description=experience["description"],
                    title = experience["title"],
                    start_date=experience_start_date,
                    end_date=experience_end_date,
                    is_current=is_experience_current
            )

            profile.save()
            
        return True

    def parse_profile_experiences(self, company, role):
        """
        Scrape all the experiences and their corresponding detail about each experience on this profile page.
        If the profile doesn't have any experience, then return None.
        :return: List of dictionaries containing information about each experience. Return None if no experience.
        """
        experiences = []
        exps = self.get_multiple_by_xpath_or_none('EXPERIENCES')
        if not exps:
            return None

        experience_with_incorrect_company= 0
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
            #NOTE: Counting number of companies that are different than the company we're looking for
            if temp['company'].lower() != company.lower():
                experience_with_incorrect_company +=1
            experiences.append(temp)

        # Handling the case when the user doesn't have any experience in the desired company (when user did not update LinkedIn yet):
        if len(experiences) == experience_with_incorrect_company:
            return None

        # NOTE: after all experiences have been scraped, check if there's an experience that match to the desired company and role:
        # for experience in experiences:
            # if experience['company'].lower() == company.lower() and role.lower() in experience['title'].lower(): 
            #     return experiences

        return experiences

    def extract_gpa(grade):
        """
        Manipulate the string form of extracted grade of education into a relative gpa number
        :return: Float number indicating the relative gpa. None if no numerical number can be found in grade.
        """
        gpas = re.findall('[0-4]\.[0-9]?[0-9]?', grade)
        if not gpas:
            return None

        gpas = map(lambda x: float(x), gpas)
        return min(gpas)

    def parse_profile_education(self):
        """
        Scrape all the education and corresponding details about each education on this profile page.
        If the profile doesn't have any education, or if the most recent education is missing school name, date range, or field of study, then return None.
        For any subsequent education that occurred earlier than the most recent education, do not add in the returning list if it's missing school name, date range, or field of study.
        :return: List of dictionaries containing information about each education. Return None if above condition does not satisfy.
        """
        educations = []
        get_educations = self.get_multiple_by_xpath_or_none("EDUCATION_MULTIPLE")
        if not get_educations: # if there isn't multiple educations, but this person has 1 education
            single_education_web_element = self.get_by_xpath_or_none("EDUCATION_SINGLE")
            if not single_education_web_element:
                return None
            get_educations = []
            get_educations.append(single_education_web_element)

        iteration = 0
        for education in get_educations:
            temp = {}
            temp["institution"] = self.element_get_text_by_xpath_or_none(
                    education, "SCHOOL") if self.element_get_text_by_xpath_or_none(education, "SCHOOL") is not None else ""
            temp["field_of_study"] = self.element_get_text_by_xpath_or_none(
                    education, "FIELD_OF_STUDY").split('\n')[1] if self.element_get_text_by_xpath_or_none(education, "FIELD_OF_STUDY") is not None else "" 
            degree = self.element_get_text_by_xpath_or_none(
                    education, "DEGREE").split('\n')[1] if self.element_get_text_by_xpath_or_none(education, "DEGREE") is not None else ""
            
            if "bachelor" in degree.lower():
                degree = "Bachelor"
            elif "master" in degree.lower():
                degree = "Master"
            elif "phd" in degree.lower():
                degree = "PhD"
            else:
                degree = "Other"

            temp["degree"] = degree
            temp["grade"] = self.element_get_text_by_xpath_or_none(
                    education, "GRADE").split('\n')[1] if self.element_get_text_by_xpath_or_none(education, "GRADE") is not None else ""
            
            start_date = ""
            end_date = ""
            school_date_range = self.element_get_text_by_xpath_or_none(
                    education, "SCHOOL_DATE_RANGE") if self.element_get_text_by_xpath_or_none(education, "SCHOOL_DATE_RANGE") is not None else ""
            if school_date_range != "":
                start_date = datetime(int(school_date_range.split('\n')[1].split(' ')[0]), 9, 1)
                try:
                    int(school_date_range.split('\n')[1].split(' ')[2])
                except IndexError:
                    school_date_range = ""
                else:
                    end_date = datetime(int(school_date_range.split('\n')[1].split(' ')[2]), 5, 1)
                
            temp["start_date"] = start_date
            temp["end_date"] = end_date

            temp["description"] = self.element_get_text_by_xpath_or_none(
                    education, "EDUCATION_DESCRIPTION") if self.element_get_text_by_xpath_or_none(education, "EDUCATION_DESCRIPTION") is not None else ""

            if iteration==0 and (temp["institution"] == "" or temp["field_of_study"] == "" or school_date_range == ""):
                return None
            elif iteration>=0 and (temp["institution"] != "" and temp["field_of_study"] != "" and school_date_range != ""):
                educations.append(temp)
            iteration+=1

        return educations