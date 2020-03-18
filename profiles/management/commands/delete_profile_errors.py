from django.core.management.base import BaseCommand, CommandError
from profiles.models import *

class Command(BaseCommand):
    help = 'delete profiles that\'s in wrong format'

    def handle(self, *args, **options):
        print("Total of {} profiles".format(len(Profile.objects.all())))
        for p in Profile.objects.all(): 
            for exp in p.experience_set.all(): 
                if not exp.company:
                    print("Deleting {} profile".format(p.username))
                    p.delete()
                    break 