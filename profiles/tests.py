from django.test import TestCase
from .models import Profile
from .scraper import LinkedInScraper
import time
from profiles.models import Profile, Education, Experience
from datetime import date, datetime


class ProfileTestCase(TestCase):
    def setUp(self):
        self.p = Profile()

    def test_prod(self):
        l = LinkedInScraper()
        

    def test_false(self):
        linkedin = LinkedInScraper()
        linkedin.login()
        print(linkedin.get_profile_by_url("https://www.linkedin.com/in/waltonwang"))
        linkedin.quit()

    def test_gpa_extractor(self):
        grades = [
            "4",
            "0.01",
            "3.99",
            "2.8fewfwe",
            "fwe4.00afwefe",
            "Fourth Year",
            "3.7/4.0",
        ]

        expected = [
            None,
            0.01,
            3.99,
            2.8,
            4.00,
            None,
            3.7
        ]
        results = [LinkedInScraper.extract_gpa(g) for g in grades]

        for i in range(len(results)):
            self.assertTrue(results[i] == expected[i])

    def test_linkedin_scraper_by_url(self):
        linkedin = LinkedInScraper()
        linkedin.login() # perhaps don't need to do linkedin login, just directly visit the page
        print(linkedin.get_profile_by_url("https://www.linkedin.com/in/joyliu3"))
        #linkedin.quit()

    # def test_profile_database(self):
    #     test_profile = Profile(name = "Joy Liu", location = "Toronto")
    #     test_profile.save()
        
    #     test_profile_experience = test_profile.experience_set.create(company = "Microsoft", description = "•Reduced average index storage space by ~20% through extraction of key-phrases in attachments stored in Dynamics365• Optimized key-phrase extraction for 1MB of text from 9 to 0.5 sec for 40+ languages using spaCy, an open-source natural language processing (NLP) library", 
    #         start_date = datetime(2019, 5, 1), end_date = datetime(2019, 8, 1), is_current = False)

    #     test_profile_education = test_profile.education_set.create(school_name = "University of Toronto", degree = "Bachelor", 
    #         field_of_study = "Computer Engineering", description = "", gpa = "3.3", 
    #         start_date = datetime(2016, 9, 1), end_date = datetime(2020, 5, 1), is_current = True)
    #     # saving the entire profile into DB 
    #     test_profile.save()

    #     print("Name: ", test_profile.name)
    #     print("Location: ", test_profile.location)
    #     print('\n', 'Experience:')
    #     print("Company: ", test_profile.experience_set.get(id=1).company)
    #     print("Description: ", test_profile.experience_set.get(id=1).description)
    #     print("Start Date: ", test_profile.experience_set.get(id=1).start_date)
    #     print("End Date: ", test_profile.experience_set.get(id=1).end_date)
    #     print('\n', "Education:")
    #     print("School Name: ", test_profile.education_set.get(id=1).school_name)
    #     print("Degree: ", test_profile.education_set.get(id=1).degree)
    #     print("Field of Study: ", test_profile.education_set.get(id=1).field_of_study)
    #     print("Description: ", test_profile.education_set.get(id=1).description)
    #     print("GPA: ", test_profile.education_set.get(id=1).gpa)
    #     print("Start Date: ", test_profile.education_set.get(id=1).start_date)
    #     print("End Date: ", test_profile.education_set.get(id=1).end_date)

    # def test_education_to_vector(self):
    #     e = Education(
    #         profile=self.p,
    #         school_name='university of toronto',
    #         degree='bachelors',
    #         field_of_study='computer engineering',
    #         description='ewf',
    #         start_date=date(2016, 9, 1),
    #         end_date=date(2020, 9, 1),
    #         is_current=True
    #     )
    #     education_vector = e.to_vector(date(2020,1,1))
    #     self.assertTrue(education_vector == [60.04, 0, 4, -1, 0.079084, -0.81504, 1.7901, 0.91653, 0.10797, -0.55628, -0.84427, -1.4951, 0.13418, 0.63627, 0.35146, 0.25813, -0.55029, 0.51056, 0.37409, 0.12092, -1.6166, 0.83653, 0.14202, -0.52348, 0.73453, 0.12207, -0.49079, 0.32533, 0.45306, -1.585, -0.63848, -1.0053, 0.10454, -0.42984, 3.181, -0.62187, 0.16819, -1.0139, 0.064058, 0.57844, -0.4556, 0.73783, 0.37203, -0.57722, 0.66441, 0.055129, 0.037891, 1.3275, 0.30991, 0.50697, 1.2357, 0.1274, -0.11434, 0.20709, -0.30847, 0.23461, 0.11819, 0.50325, -0.4622, 0.33465, -0.24591, -0.90292, 0.39837, -0.3622, 1.0792, 0.22552, -0.60442, -0.30231, -1.41, -0.22967, -0.075232, 1.8487, -0.23882, -0.21088, 1.3641, 0.4565, -0.75138, -1.007, -0.029306, -0.94489, -0.86208, -1.4729, -0.98162, 0.25306, 2.6589, -0.48034, 0.020104, -1.063, 0.71672, 0.5565, -0.42515, 1.3095, 1.4427, 0.51156, -0.022319, -1.0668, 0.39002, 0.16765, 0.045271, 0.2151, 0.49155, 0.78136, -0.31409, 0.05833, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

# Create your tests here.
