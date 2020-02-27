import time
from random import uniform

def random_sleep(seconds, delta):
    secs = uniform(seconds - delta, seconds + delta)
    time.sleep(secs)