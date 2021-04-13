#!/usr/bin/env python
# headfinder.py

import pandas as pd
import argparse

import spacy

nlp = spacy.load("en_core_web_lg")

"""
Returns the syntactic head of the phrase using spaCy's dependency
parser, if it exists. Returns None otherwise.
"""
def get_head(phrase):
    doc = nlp(phrase)
    sents = list(doc.sents)
    if sents != []:
        return str(list(doc.sents)[0].root)


'''
Parse command-line arguments.
'''
def get_args():
    parser = argparse.ArgumentParser(
        description='Get coordination stats from csv input file(s) containing parsed sentences.')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input csv file(s)')
    return parser.parse_args()


'''
Main function.
'''
if __name__ == "__main__":

    args = get_args()

    i = 1
    tot = str(len(args.input_files))

    for file in args.input_files:

        print("(" + str(i) + "/" + tot + ")")
        print("Finding heads of conjuncts in " + file + "...")

        df = pd.read_csv(file)

        df['1st Conjunct Head'] = df.apply(
            lambda row: get_head(str(row['1st Conjunct Text'])), axis=1)
        df['2nd Conjunct Head'] = df.apply(
            lambda row: get_head(str(row['2nd Conjunct Text'])), axis=1)

        dest = file.replace('_ccps', '_heads')
        df.to_csv(dest, index=False)

        print("All done! The result is stored in " + dest + ".\n")
        i = i + 1
