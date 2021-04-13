#!/usr/bin/env python
# wordnet_relations.py

from nltk.corpus import wordnet as wn
import argparse
import pandas as pd


NOUN_CATEGORIES = ['NN', 'NNS', 'NNP', 'NNPS', 'NP', 'NX']
VERB_CATEGORIES = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VP']
ADJ_CATEGORIES = ['JJ', 'JJR', 'JJS', 'ADJP']
ADV_CATEGORIES = ['RB', 'RBR', 'RBS', 'ADVP']


def get_wordnet_tag(nltk_tag):
    """
    Return the equivalent wordnet POS tag for the given nltk
    POS tag.
    """
    if nltk_tag in ADJ_CATEGORIES:
        return wn.ADJ
    elif nltk_tag in VERB_CATEGORIES:
        return wn.VERB
    elif nltk_tag in NOUN_CATEGORIES:
        return wn.NOUN
    elif nltk_tag in ADV_CATEGORIES:
        return wn.ADV
    else:
        # Use noun as a default POS tag in lemmatization
        return wn.NOUN


def synonyms(word1, word2, tag):
    """
    Returns whether word1 and word2 are synonyms by testing all possible
    synsets of word1 and word2.
    """
    pos = get_wordnet_tag(tag)
    return not set(wn.synsets(word1, pos=pos)).isdisjoint(set(wn.synsets(word2, pos=pos)))


def antonyms(word1, word2, tag):
    """
    Returns whether word1 is an antonym of word2 by testing all possible
    synsets of word1 and word2.
    """
    pos = get_wordnet_tag(tag)

    # Test relation among all pairs of synsets
    synsets1 = set([l for s in wn.synsets(word1, pos=pos) for l in s.lemmas()])
    for ss in wn.synsets(word2, pos=pos):
        for l in ss.lemmas():
            antonyms = l.antonyms()
            if not synsets1.isdisjoint(antonyms):
                return True

    return False


def relates(word1, word2, rel, tag):
    """
    Returns whether word1 relates to word2 by testing all possible
    synsets of word1 and word2, using the given relation function.
    """
    pos = get_wordnet_tag(tag)

    # Test relation among all pairs of synsets
    synsets1 = set(wn.synsets(word1, pos=pos))
    for ss in wn.synsets(word2, pos=pos):
        relations = set([i for i in ss.closure(rel)])
        if not synsets1.isdisjoint(relations):
            return True

    return False


def is_hypernym(word1, word2, tag):
    """
    Returns whether word1 is a hypernym of word2 by testing all possible
    synsets of word1 and word2.
    """
    return relates(word1, word2, lambda s: s.hypernyms(), tag)


def get_co_hyponyms(synset):
    """
    Returns co_hyponyms of the given synset.
    """
    co_hyponyms = set()
    for hyper in synset.hypernyms():
        for hypo in hyper.hyponyms():
            co_hyponyms.add(hypo)
    return co_hyponyms


def co_hyponyms(word1, word2, tag):
    """
    Returns whether word1 and word2 are co-hyponyms by testing all possible
    synsets of word1 and word2.
    """
    pos = get_wordnet_tag(tag)

    # Test relation among all pairs of synsets
    synsets = set(wn.synsets(word1, pos=pos))
    for ss in wn.synsets(word2, pos=pos):
        co_hyponyms = get_co_hyponyms(ss)
        if not synsets.isdisjoint(co_hyponyms):
            return True

    return False


def entails(word1, word2, tag):
    """
    Returns whether word1 entails word2 by testing all possible
    synsets of word1 and word2.
    """

    return relates(word2, word1, lambda s: s.entailments(), tag)


def analyze_synonymy(file):
    """
    Run synonymy analysis on all categories in the given csv file.
    Output written to a file "_syns.csv".
    """

    df = pd.read_csv(file)

    df = df[(df['1st Conjunct Category'].isin(NOUN_CATEGORIES) & df['2nd Conjunct Category'].isin(NOUN_CATEGORIES)) |
            (df['1st Conjunct Category'].isin(VERB_CATEGORIES) & df['2nd Conjunct Category'].isin(VERB_CATEGORIES)) |
            (df['1st Conjunct Category'].isin(ADJ_CATEGORIES) & df['2nd Conjunct Category'].isin(ADJ_CATEGORIES)) |
            (df['1st Conjunct Category'].isin(ADV_CATEGORIES) & df['2nd Conjunct Category'].isin(ADV_CATEGORIES))]

    df['Synonyms?'] = df.apply(lambda row: synonyms(
        str(row['1st Conjunct Head']),
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)

    dest = file.replace('_heads', '_syns')
    df.to_csv(dest, index=False)

    print("Synonymy analysis done! Result stored in " + dest + ".")


def analyze_antonymy(file):
    """
    Run antonymy analysis on adjective and adverb-like categories
    in the given csv file. Output written to a file "_ants.csv".
    """

    df = pd.read_csv(file)

    df = df[(df['1st Conjunct Category'].isin(ADJ_CATEGORIES) & df['2nd Conjunct Category'].isin(ADJ_CATEGORIES)) |
            (df['1st Conjunct Category'].isin(ADV_CATEGORIES) & df['2nd Conjunct Category'].isin(ADV_CATEGORIES))]

    df['Antonyms?'] = df.apply(lambda row: antonyms(
        str(row['1st Conjunct Head']),
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)

    dest = file.replace('_heads', '_ants')
    df.to_csv(dest, index=False)

    print("Antonymy analysis done! Result stored in " + dest + ".")


def analyze_hypernymy(file):
    """
    Run hypernymy and co-hyponymy analysis on noun-like and verb-like
    categories in the given csv file. Output written to a file "_hyp.csv".
    """

    df = pd.read_csv(file)

    df = df[(df['1st Conjunct Category'].isin(NOUN_CATEGORIES) & df['2nd Conjunct Category'].isin(NOUN_CATEGORIES)) |
            (df['1st Conjunct Category'].isin(VERB_CATEGORIES) & df['2nd Conjunct Category'].isin(VERB_CATEGORIES))]

    df['1st Conjunct Hypernym?'] = df.apply(lambda row: is_hypernym(
        str(row['1st Conjunct Head']),
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)
    df['2nd Conjunct Hypernym?'] = df.apply(lambda row: is_hypernym(
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)

    df['Co-hyponyms?'] = df.apply(lambda row: co_hyponyms(
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)

    dest = file.replace('_heads', '_hyp')
    df.to_csv(dest, index=False)

    print("Hypernymy and co-hyponymy analysis done! Result stored in " + dest + ".")


def analyze_entailment(file):
    """
    Run entailment analysis on verb-like categories in the given csv file.
    Output written to a file "_entl.csv".
    """

    df = pd.read_csv(file)

    df = df[df['1st Conjunct Category'].isin(VERB_CATEGORIES)]
    df = df[df['2nd Conjunct Category'].isin(VERB_CATEGORIES)]

    df['1st Conjunct Entails 2nd?'] = df.apply(lambda row: entails(
        str(row['1st Conjunct Head']),
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)
    df['2nd Conjunct Entails 1st?'] = df.apply(lambda row: entails(
        str(row['2nd Conjunct Head']),
        str(row['1st Conjunct Head']),
        str(row['1st Conjunct Category'])), axis=1)

    dest = file.replace('_heads', '_entl')
    df.to_csv(dest, index=False)

    print("Entailment analysis done! Result stored in " + dest + ".")


def get_args():
    '''
    Parse command-line arguments.
    '''

    parser = argparse.ArgumentParser(
        description='Get wordnet relation stats from csv input file(s).')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input csv file(s)')
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Main function.
    '''

    args = get_args()

    i = 1
    tot = str(len(args.input_files))

    for file in args.input_files:

        print("(" + str(i) + "/" + tot + ")")
        print("Measuring wordnet relations of conjuncts in " + file + "...")

        analyze_synonymy(file)
        analyze_antonymy(file)
        analyze_hypernymy(file)
        analyze_entailment(file)

        i = i + 1
