from .constants import school_scores
from django.conf import settings
from utils.glove_loader import load_glove_model

GLOVE_FILE = 'utils/glove.6B.50d.txt'
SCHOOL_DEFAULT_SCORE = 30

if settings.DEBUG:
    GLOVE_FILE = 'utils/dev_word_embeddings.txt'

glove = load_glove_model(GLOVE_FILE)

class School:
    def __init__(self, school_name):
        self.school_name = school_name.lower()
    
    def to_vector(self):
        return [school_scores.get(self.school_name, SCHOOL_DEFAULT_SCORE)]

class StudyField:
    """
    Field of study of education, examples: computer engineering, psycology
    """
    def __init__(self, field_of_study):
        self.field_of_study = self.process_field_of_study(field_of_study)

    def process_field_of_study(self, field_of_study):
        """
        """
        field = field_of_study.split()[:3]
        padding = 3 - len(field)
        field = field + [''] * (padding * 50)
        return field
        
    def to_vector(self):
        return glove.get(self.field_of_study[0], [0] * 50) \
                + glove.get(self.field_of_study[1], [0] * 50) \
                + glove.get(self.field_of_study[2], [0] * 50)
