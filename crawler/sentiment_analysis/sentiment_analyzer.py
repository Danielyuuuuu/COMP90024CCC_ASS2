import pandas as pd
import re
import pickle

from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

# nltk
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import os


class SentimentAnalyzer:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.lemmatizer = WordNetLemmatizer()
        self.model = keras.models.load_model(os.path.join(dir_path, 'nlp.model'))
        with open(os.path.join(dir_path, 'word_tokenizer.pkl'), 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    # function to convert nltk tag to wordnet tag
    def nltk_tag_to_wordnet_tag(self, nltk_tag):
        if nltk_tag.startswith('J'):
            return wordnet.ADJ
        elif nltk_tag.startswith('V'):
            return wordnet.VERB
        elif nltk_tag.startswith('N'):
            return wordnet.NOUN
        elif nltk_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def lemmatize_sentence(self, sentence):
        # tokenize the sentence and find the POS tag for each token
        nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))

        wordnet_tagged = map(lambda x: (x[0], self.nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)
        lemmatized_sentence = []
        for word, tag in wordnet_tagged:
            if tag is None:
                lemmatized_sentence.append(word)
            else:
                lemmatized_sentence.append(self.lemmatizer.lemmatize(word, tag))
        return " ".join(lemmatized_sentence)

    def clean_tweet_text(self, text):
        return re.sub(r"[^\w\d'\s]+", ' ', re.sub("@[^\s]+|https?:\S+|http?:\S", ' ', str(text).lower()))

    def predict_sentiment(self, text):
        clean = self.clean_tweet_text(text)
        lemma = self.lemmatize_sentence(clean)
        score = self.model.predict([pad_sequences(self.tokenizer.texts_to_sequences([lemma]), maxlen=140)])[0][0]
        if score >= 0.66:
            senti = 'Positive'
        elif score < 0.33:
            senti = 'Negative'
        else:
            senti = 'Neutral'
        return (score, senti)
