from django.core.management.base import BaseCommand, CommandError
from profiles.models import *
from profiles.scraper import *               
from profiles.linkedin import *

class Command(BaseCommand):
    help = 'Ingest LinkedIn profiles {company(period separated} {title{period separated' \
        + 'Ex: python manage.py ingest_profiles 19 google software.engineer'

    def add_arguments(self, parser):
        parser.add_argument('num_employees', nargs='?', type=int)
        parser.add_argument('company', nargs='?', type=str)
        parser.add_argument('title', nargs='?', type=str)

    def handle(self, *args, **options):
        company = ' '.join(options['company'].split('.'))
        title = ' '.join(options['title'].split('.'))
        num_employees = options['num_employees']
        ll = LinkedInScraper()
        li = LinkedIn(ll)

        li.get_profiles(company, title, num_employees)
        ll.quit()