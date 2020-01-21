from django.apps import AppConfig
import threading
import sys

class PostingsConfig(AppConfig):
    name = 'postings'

    def ready(self):
        print(sys.argv)
        if 'gunicorn' in sys.argv[0].split('/'):
            # Can only be imported here
            from .ingestions import repeat 
            t = threading.Thread(target=repeat)
            t.daemon = True
            t.start()