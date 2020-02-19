from django.conf import settings

## Profiles
WORD_EMBEDDING_LEN = 50

# Educatikon
SCHOOL_VEC_LEN = 1
EDUCATION_VECTOR_LEN = WORD_EMBEDDING_LEN*3 + SCHOOL_VEC_LEN + 3

# Experience
NUM_EXPERIENCE_TITLE_WORDS = 4
PREV_YEARS_LOOKUP = 10
# Num months worked in that year
EXPERIENCE_YEAR_VECTOR_LEN = WORD_EMBEDDING_LEN*NUM_EXPERIENCE_TITLE_WORDS + 1
EXPERIENCE_VECTOR_LEN = EXPERIENCE_YEAR_VECTOR_LEN * PREV_YEARS_LOOKUP

GLOVE_FILE = 'utils/dev_word_embeddings.txt'
# GLOVE_FILE = 'utils/glove.6B.50d.txt'
# if settings.DEBUG:
#     GLOVE_FILE = 'utils/dev_word_embeddings.txt'