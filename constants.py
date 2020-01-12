from django.conf import settings

WORD_EMBEDDING_LEN = 50
SCHOOL_VEC_LEN = 1
EDUCATION_VECTOR_LEN = WORD_EMBEDDING_LEN*3 + SCHOOL_VEC_LEN + 3

PREV_YEARS_LOOKUP = 10

GLOVE_FILE = 'utils/glove.6B.50d.txt'
if settings.DEBUG:
    GLOVE_FILE = 'utils/dev_word_embeddings.txt'