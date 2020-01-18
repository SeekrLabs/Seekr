from utils.glove import Glove
from constants import *
import sys

if any(command in sys.argv for command in ['runserver', 'shell', 'test']):
    glove = Glove(GLOVE_FILE)
else:
    glove = None