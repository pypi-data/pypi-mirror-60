from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

punctuations = ['(', ')', ';', ':', '[', ']', ',']


def get_words(text, language="english"):
    tokens = word_tokenize(text)

    stop_words = stopwords.words(language)
    keywords = [word for word in tokens if not word in stop_words and not word in punctuations]
    return keywords
