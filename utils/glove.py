from constants import *

class Glove:
    def __init__(self, glove_file):
        print("Loading Glove Model")
        f = open(glove_file,'r')
        self.model = {}
        for line in f:
            splitLine = line.split()
            word = splitLine[0]
            embedding = [float(val) for val in splitLine[1:]]
            self.model[word] = embedding
        
        assert(WORD_EMBEDDING_LEN == len(self.model[word]))
        print("Done.",len(self.model)," words loaded!")

    def get_string_embedding(self, s, num_words):
        # Parse string
        words = s.split()[:num_words]
        
        # Pad if less than num_words
        padding = num_words - len(words)
        words = words + [''] * (padding * WORD_EMBEDDING_LEN)
        
        res = []
        for w in words:
            res += self.model.get(word, [0] * WORD_EMBEDDING_LEN)
        
        return res

    
