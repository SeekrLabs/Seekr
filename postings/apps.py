from django.apps import AppConfig
import threading
import sys

class PostingsConfig(AppConfig):
    name = 'postings'

    def ready(self):
        if 'runserver' in sys.argv:
            # Can only be imported here
            from .ingestions import repeat 
            t = threading.Thread(target=repeat)
            t.daemon = True
            t.start()