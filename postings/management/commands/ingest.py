from django.core.management.base import BaseCommand, CommandError
from postings.ingestions import IndeedIngestion
from constants import CANADA_LOCATIONS, US_LOCATIONS, TITLES

class Command(BaseCommand):
    help = 'Initial ingestion command'

    def add_arguments(self, parser):
        parser.add_argument('num_pages', nargs='?', type=int)

    def handle(self, *args, **options):
        indeed = IndeedIngestion(ca_locations=CANADA_LOCATIONS,
            us_locations=US_LOCATIONS,
            titles = TITLES)
        indeed.ingest_jobs(options['num_pages'])