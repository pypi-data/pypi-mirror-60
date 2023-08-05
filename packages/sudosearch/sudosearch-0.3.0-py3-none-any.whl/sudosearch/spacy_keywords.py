import spacy

from collections import Counter
from string import punctuation

class Keywords:
    '''
    Keywords Object using Spacy
    '''

    __nlp = None

    __tags = ['PROPN', 'ADJ', 'NOUN']

    def __init__(self):
        '''
        Class construct
        '''
        self.__nlp = spacy.load('en_core_web_lg')

    def get_hotties(self, text, count = None):
        '''
        Get hot words from text

        Params:
            self    Keywords

        '''

        result = []
        doc = self.__nlp(text.lower())

        for token in doc:
            if(token.text in self.__nlp.Defaults.stop_words or token.text in punctuation):
                continue
            
            if(token.pos_ in self.__tags):
                result.append(token.text)
        
        if not count == None:
            return Counter(set(result)).most_common(count)

        return result
