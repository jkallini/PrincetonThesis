#!/usr/bin/env python
# ccpfinder.py
# Read each row of the csv passed as a command-line argument. csv
# must have two columns: "Sentence Text", and "Sentence Parse Tree".
# This script iterates over all rows and find the two-termed coordination
# phrases in the parse trees. If the input is named 'sample.csv' (or
# the result is written to 'sample_ccps.csv'.

import pandas as pd
import os
import argparse
import re

from nltk import ParentedTree

from tqdm import tqdm


nor_pattern = re.compile(r'^neither.*nor.*')


def get_tree_text(tree):
    '''
    Function: Get the sentence text of the given NLTK tree.
    Input: NLTK tree
    Output: sentence string
    '''
    return " ".join(tree.leaves())


def get_simple_coordphrases(tree):
    '''
    Function: Find all simple coordination phrases of the given NLTK tree.
    Input: NLTK tree
    Output:
        list of phrases
        a phrase is a 3 tuple containing the first conjunct (string),
        a conjunction (string), and a second conjunct (string)
    '''

    phrases = []

    for s in tree.subtrees(
            lambda t: t.label() == "CC" and
            (len(list(t.parent())) == 3 or len(list(t.parent())) == 4)):

        parent = s.parent()
        
        # Simple three-prong coordination phrases
        if len(list(parent)) == 3:
            # Get left ad right siblings
            left = s.left_sibling()
            right = s.right_sibling()

            if left is None or right is None:
                continue

            conjunct1 = (left.label(), get_tree_text(left))
            conjunct2 = (right.label(), get_tree_text(right))
            conjunction = get_tree_text(s)
            phrases.append((conjunct1, conjunction, conjunct2))

        # "neither-nor" coordination phrases
        elif get_tree_text(parent[0]) == 'neither' and get_tree_text(parent[2]) == 'nor':
            left = parent[1]
            right = parent[3]
            conjunct1 = (left.label(), get_tree_text(left))
            conjunct2 = (right.label(), get_tree_text(right))
            conjunction = 'nor'
            phrases.append((conjunct1, conjunction, conjunct2))

        # VPs with both conjuncts as complements
        elif parent.label() == 'VP' and parent[2].label() == 'CC':
            left = parent[1]
            right = parent[3]
            conjunct1 = (left.label(), get_tree_text(left))
            conjunct2 = (right.label(), get_tree_text(right))
            conjunction = get_tree_text(parent[2])
            phrases.append((conjunct1, conjunction, conjunct2))            

    return phrases


def get_args():
    '''
    Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Get coordination stats from csv input file(s) containing parsed sentences.')
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
        print("Gathering coordination stats from " + file + "...")

        sents = pd.read_csv(file)
        data = []

        for index, row in tqdm(sents.iterrows(), total=len(sents.index)):
            parse_tree = row["Sentence Parse Tree"]
            tree = ParentedTree.fromstring(parse_tree)
            sent = get_tree_text(tree)
            for coord in get_simple_coordphrases(tree):
                category1 = coord[0][0]
                conjunct1 = coord[0][1]
                conjunction = coord[1]
                category2 = coord[2][0]
                conjunct2 = coord[2][1]
                data.append([category1, conjunct1, category2, conjunct2,
                             conjunction, sent, parse_tree])

        columns = ['1st Conjunct Category', '1st Conjunct Text',
                   '2nd Conjunct Category', '2nd Conjunct Text',
                   'Conjunction', 'Sentence Text', 'Sentence Parse Tree']
        df = pd.DataFrame(data, columns=columns)
        df.drop_duplicates(inplace=True)
        df.reset_index(inplace=True, drop=True)

        dest = os.path.splitext(file)[-2] + '_ccps.csv'
        df.to_csv(dest, index=False)

        print("All done! The result is stored in " + dest + ".\n")
        i = i + 1
