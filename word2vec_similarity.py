#!/usr/bin/env python
# word2vec_similarity.py
# Utilizes Google's pre-trained word embeddings: https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit
# Adapted from: https://github.com/Lipairui/Text-similarity-centroid-of-the-word-vectors

import gensim
from nltk.corpus.reader.wordnet import NOUN
import numpy as np
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords, wordnet
from sklearn.metrics.pairwise import cosine_similarity
import argparse
import pandas as pd
from nltk.stem import WordNetLemmatizer


# Load Google's pre-trained Word2Vec model.
model = gensim.models.KeyedVectors.load_word2vec_format(
    './word2vec/GoogleNews-vectors-negative300.bin', binary=True)

# Most important categories for word similarity
NOUN_CATEGORIES = ['NN', 'NNS', 'NNP', 'NNPS', 'NX', 'NP']
VERB_CATEGORIES = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VP']
ADJ_CATEGORIES = ['JJ', 'JJR', 'JJS', 'ADJP']
ADV_CATEGORIES = ['RB', 'RBR', 'RBS', 'ADVP']
CATEGORIES = NOUN_CATEGORIES + VERB_CATEGORIES + ADJ_CATEGORIES + ADV_CATEGORIES

lemmatizer = WordNetLemmatizer()


# function to convert nltk tag to wordnet tag
def nltk_tag_to_wordnet_tag(nltk_tag):
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


# function to convert ptb tag to wordnet tag
def ptb_tag_to_wordnet_tag(ptb_tag):
    if ptb_tag in ADJ_CATEGORIES:
        return wordnet.ADJ
    elif ptb_tag in VERB_CATEGORIES:
        return wordnet.VERB
    elif ptb_tag in NOUN_CATEGORIES:
        return wordnet.NOUN
    elif ptb_tag in ADV_CATEGORIES:
        return wordnet.ADV
    else:
        return None


def lemmatize_sentence(sentence):
    # tokenize the sentence and find the POS tag for each token
    nltk_tagged = pos_tag(word_tokenize(sentence))
    # tuple of (token, wordnet_tag)
    wordnet_tagged = map(lambda x: (
        x[0], nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)
    lemmatized_sentence = []
    for word, tag in wordnet_tagged:
        if tag is None:
            # if there is no available tag, append the token as is
            lemmatized_sentence.append(word)
        else:
            # else use the tag to lemmatize the token
            lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))
    return lemmatized_sentence


'''
Function: preprocess doc including cleaning, tokenzing, lemmatizing...
Input: document string
Output: list of words
'''
def preprocess(doc):
    sw = set(stopwords.words('english'))
    doc = doc.lower()
    doc = lemmatize_sentence(doc)
    doc = [word for word in doc if word not in sw]
    doc = [word for word in doc if word.isalpha()]
    return doc


'''
Function: compute the mean of word vectors.
Input: list of words
Output: doc vector 
'''
def doc_vector(doc):
    # remove out-of-vocab words
    doc = [word for word in doc if word in model.vocab]
    return np.mean(model[doc], axis=0)


'''
Function: check if a document has a vector representation.
Input: list of words
Output:
  Boolean value:
    True: doc is not null and has vector representation
    False: doc is null or has no vector representation
'''
def has_representation(doc):
    if len(doc) == 0:
        # check if doc is null
        return False
    else:
        # check if at least one word of the document is in the word2vec dictionary
        return not all(word not in model.vocab for word in doc)


'''
Function: calculate cosine similarity of document pair.
Input: 
  doc1: list of words of document1
  doc2: list of words of document2
Output:
  similarity of doc1 and doc2: (float)
  value ranges from 0 to 1;
  -1 means error
'''
def calculate_similarity(doc1, doc2):
    # check representations
    if not has_representation(doc1) or not has_representation(doc2):
        # if any of the two documents does not have representation
        return -1
    else:
        vec1 = np.array(doc_vector(doc1)).reshape(1, -1)
        vec2 = np.array(doc_vector(doc2)).reshape(1, -1)
        cos = cosine_similarity(vec1, vec2)[0][0]
        # regularize value of cos to [-1,1]
        if cos < -1.0:
            cos = -1.0
        if cos > 1.0:
            cos = 1.0
        sim = 1-np.arccos(cos)/np.pi
        return sim


'''
Function: compute similarity between the two documents.
Input:
  doc1: document string
  doc2: document string
Output:
  similarity of doc1 and doc2: (float)
  value ranges from 0 to 1
  None means error
'''
def doc_similarity(doc1, doc2):
    # Preprocess docs
    d1 = preprocess(doc1)
    d2 = preprocess(doc2)
    sim = calculate_similarity(d1, d2)
    if sim < 0:
        return None
    else:
        return sim


def word_similarity(word1, cat1, word2, cat2):
    word1 = word1.lower()
    word2 = word2.lower()

    lemma1 = lemmatizer.lemmatize(word1, ptb_tag_to_wordnet_tag(cat1))
    lemma2 = lemmatizer.lemmatize(word2, ptb_tag_to_wordnet_tag(cat2))

    if lemma1 in model.vocab and lemma2 in model.vocab:
        return model.similarity(lemma1, lemma2)

    return None


'''
Parse command-line arguments.
'''
def get_args():
    parser = argparse.ArgumentParser(
        description='Get wordnet relation stats from csv input file(s).')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input csv file(s)')
    return parser.parse_args()


def measure_docsim(file):
    print("Getting document similarity of conjuncts in " + file + "...")

    df = pd.read_csv(file)

    df['Document Similarity'] = df.apply(lambda row: doc_similarity(
        str(row['1st Conjunct Text']), str(row['2nd Conjunct Text'])), axis=1)

    dest = file.replace('_heads', '_docsim')
    df.to_csv(dest, index=False)

    print("Document similarity analysis done! Result stored in " + dest + ".")


def measure_sim(file):
    print("Getting head similarity of conjuncts in " + file + "...")

    df = pd.read_csv(file)

    df = df[df['1st Conjunct Category'].isin(CATEGORIES)]
    df = df[df['2nd Conjunct Category'].isin(CATEGORIES)]

    df['Similarity'] = df.apply(lambda row: word_similarity(
        str(row['1st Conjunct Head']),
        str(row['1st Conjunct Category']),
        str(row['2nd Conjunct Head']),
        str(row['2nd Conjunct Category']),
    ), axis=1)

    dest = file.replace('_heads', '_sim')
    df.to_csv(dest, index=False)

    print("Similarity analysis done! Result stored in " + dest + ".")


'''
Main function.
'''
if __name__ == "__main__":

    args = get_args()

    i = 1
    tot = str(len(args.input_files))

    for file in args.input_files:

        print("(" + str(i) + "/" + tot + ")")

        # measure_docsim(file)
        measure_sim(file)

        i = i + 1
