#!/usr/bin/env python
# evalresults.py

import pandas as pd
from collections import defaultdict

import argparse

CATEGORIES = ['NP', 'VP', 'PP', 'ADJP', 'ADVP', 'SBAR']

NOUN_CATEGORIES = ['NN', 'NNS', 'NNP', 'NNPS', 'NP', 'NX']
VERB_CATEGORIES = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VP']
ADJ_CATEGORIES = ['JJ', 'JJR', 'JJS', 'ADJP']
ADV_CATEGORIES = ['RB', 'RBR', 'RBS', 'ADVP']

def df_from_files(files):
    '''
    Concatenate all CSV files in the files list into one dataframe.
    '''

    li = []
    for filename in files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    if li == []:
        return None

    df = pd.concat(li, axis=0, ignore_index=True)
    return df


def likes_df(df):
    nouns = df[(df['1st Conjunct Category'].isin(NOUN_CATEGORIES)) & (
        df['2nd Conjunct Category'].isin(NOUN_CATEGORIES))]

    verbs = df[(df['1st Conjunct Category'].isin(VERB_CATEGORIES)) & (
        df['2nd Conjunct Category'].isin(VERB_CATEGORIES))]

    adjps = df[(df['1st Conjunct Category'].isin(ADJ_CATEGORIES)) & (
        df['2nd Conjunct Category'].isin(ADJ_CATEGORIES))]

    advps = df[(df['1st Conjunct Category'].isin(ADV_CATEGORIES)) & (
        df['2nd Conjunct Category'].isin(ADV_CATEGORIES))]

    pps = df[(df['1st Conjunct Category'] == 'PP') & (
        df['2nd Conjunct Category'] == 'PP')]

    sbars = df[(df['1st Conjunct Category'] == 'SBAR') & (
        df['2nd Conjunct Category'] == 'SBAR')]

    likes = pd.concat([nouns, verbs, adjps, advps, pps, sbars],
                      axis=0, ignore_index=True)

    correct = likes[likes['Correct?']]

    print ("Likes:", round(len(correct.index) / len(likes.index), 4))


def unlikes_dfs(df):
    df = df[df['1st Conjunct Category'].isin(CATEGORIES)]
    df = df[df['2nd Conjunct Category'].isin(CATEGORIES)]

    # Get unlike category combinations
    unlikes = df.loc[df['1st Conjunct Category']
                     != df['2nd Conjunct Category']]

    for cat1 in CATEGORIES:
        for cat2 in CATEGORIES:
            if cat1 != cat2:
                freqs = unlikes.loc[(unlikes['1st Conjunct Category'] == cat1) & (
                    unlikes['2nd Conjunct Category'] == cat2)]
                correct = freqs[freqs['Correct?']]
                print(cat1 + '+' + cat2 + ':', round(len(correct.index) / len(freqs.index), 4))


def aggr_results():
    file1 = open('ratings/student_summary.txt', 'r')
    file2 = open('ratings/julie_summary.txt', 'r')
    file3 = open('ratings/aryan_summary.txt', 'r')

    lines1 = file1.readlines()
    lines2 = file2.readlines()
    lines3 = file3.readlines()

    for i in range(len(lines1)):
        cat = lines1[i].split(" ")[0]

        assert(cat == lines2[i].split(" ")[0])
        assert(cat == lines3[i].split(" ")[0])

        n1 = float(lines1[i].split(" ")[1].strip())
        n2 = float(lines2[i].split(" ")[1].strip())
        n3 = float(lines3[i].split(" ")[1].strip())
        print(cat, round((n1 + n2 + n3) / 3.0, 4))


def get_args():
    '''
    Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Tabulate correct coordinations from each category.')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input csv file(s)')
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Main function.
    '''

    args = get_args()

    df = df_from_files(args.input_files)

    likes_df(df)
    unlikes_dfs(df)