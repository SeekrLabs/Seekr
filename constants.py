from django.conf import settings

## Profiles
WORD_EMBEDDING_LEN = 50

# Education
SCHOOL_VEC_LEN = 1
EDUCATION_VECTOR_LEN = WORD_EMBEDDING_LEN*3 + SCHOOL_VEC_LEN + 3

# Experience
NUM_EXPERIENCE_TITLE_WORDS = 4
PREV_YEARS_LOOKUP = 10
# Num months worked in that year
EXPERIENCE_YEAR_VECTOR_LEN = WORD_EMBEDDING_LEN*NUM_EXPERIENCE_TITLE_WORDS + 1
EXPERIENCE_VECTOR_LEN = EXPERIENCE_YEAR_VECTOR_LEN * PREV_YEARS_LOOKUP

# Boto3 keys definition
AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']

SKILLS_LEN = 132

GLOVE_FILE = 'data/filtered.glove.6B.50d.txt'
if settings.DEBUG:
    GLOVE_FILE = 'data/dev_word_embeddings.txt'

HOST_URL = 'ec2-3-82-225-241.compute-1.amazonaws.com/'

BASE_LINKEDIN_USER_URL = 'https://www.linkedin.com/in/'
STOCK_IMAGE_URL = 'https://blog.herzing.ca/hubfs/becoming%20a%20programmer%20analyst%20lead-1.jpg'

US_LOCATIONS = []
CANADA_LOCATIONS = ['toronto']
TITLES = ['software engineer']
