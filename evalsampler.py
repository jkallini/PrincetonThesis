#!/usr/bin/env python
# evalsampler.py

import pandas as pd
import math
import os

import argparse


CONJUNCTIONS = ['and', 'or', 'but', 'nor']
CATEGORIES = ['NP', 'VP', 'PP', 'ADJP', 'ADVP', 'SBAR']

NOUN_CATEGORIES = ['NN', 'NNS', 'NNP', 'NNPS', 'NP', 'NX']
VERB_CATEGORIES = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VP']
ADJ_CATEGORIES = ['JJ', 'JJR', 'JJS', 'ADJP']
ADV_CATEGORIES = ['RB', 'RBR', 'RBS', 'ADVP']

# SUPPORTED CONFIDENCE LEVELS: 50%, 68%, 90%, 95%, and 99%
CONFIDENCE_LEVELS = [50, .67], [68, .99], [90, 1.64], [95, 1.96], [99, 2.57]


def sample_size(population_size, confidence_level, confidence_interval):
    '''
    Calculate the appropriate sample size from the given population size,
    confidence level, and confidence interval.

    Script from http://veekaybee.github.io/how-big-of-a-sample-size-do-you-need/
    on how to calculate sample size, adjusted for my own population size and
    confidence intervals.

    Original here: http://bc-forensics.com/?p=15
    '''

    Z = 0.0
    p = 0.5
    e = confidence_interval/100.0
    N = population_size
    n_0 = 0.0
    n = 0.0

    # LOOP THROUGH SUPPORTED CONFIDENCE LEVELS AND FIND THE NUM STD
    # DEVIATIONS FOR THAT CONFIDENCE LEVEL
    for i in CONFIDENCE_LEVELS:
        if i[0] == confidence_level:
            Z = i[1]

    if Z == 0.0:
        return -1

    # CALC SAMPLE SIZE
    n_0 = ((Z**2) * p * (1-p)) / (e**2)

    # ADJUST SAMPLE SIZE FOR FINITE POPULATION
    n = n_0 / (1 + ((n_0 - 1) / float(N)))

    return int(math.ceil(n))  # THE SAMPLE SIZE


def unlikes_dfs(df):
    df = df[df['Conjunction'].isin(CONJUNCTIONS)]
    df = df[df['1st Conjunct Category'].isin(CATEGORIES)]
    df = df[df['2nd Conjunct Category'].isin(CATEGORIES)]

    # Get unlike category combinations
    unlikes = df.loc[df['1st Conjunct Category']
                     != df['2nd Conjunct Category']]

    combs = []
    for cat1 in CATEGORIES:
        for cat2 in CATEGORIES:
            if cat1 != cat2:
                freqs = unlikes.loc[(unlikes['1st Conjunct Category'] == cat1) & (
                    unlikes['2nd Conjunct Category'] == cat2)]
                combs.append((cat1 + ' + ' + cat2, freqs))

    return combs


def likes_df(df):
    df = df[df['Conjunction'].isin(CONJUNCTIONS)]

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
    likes.reset_index(drop=True, inplace=True)

    return likes


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


def get_args():
    '''
    Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Sample coordinations from input csv input file(s).')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input csv file(s)')
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Main function.
    '''

    args = get_args()

    df = df_from_files(args.input_files)

    # Get like and unlike dfs
    unlike_dfs = unlikes_dfs(df)
    likes_df = likes_df(df)

    sampled_dfs = []

    # Sample list of unlike coordinations
    for comb,comb_df in unlike_dfs:

        # Deterine sample size based on population (length of
        # df), 90% confidence level 8% confidence interval
        n = sample_size(len(comb_df.index), 90, 8)
        sampled = comb_df.sample(n=n)
        print(comb + ':', 'N='+str(len(comb_df.index)), 'n='+str(n))
        sampled.reset_index(drop=True, inplace=True)
        sampled_dfs.append(sampled)

    # Sample like coordinations
    n = sample_size(len(likes_df), 95, 5)
    sampled = likes_df.sample(n=n)
    sampled.reset_index(drop=True, inplace=True)
    sampled = sampled.sort_values(
        ["1st Conjunct Category", "2nd Conjunct Category"], ascending=(True, True))
    sampled_dfs.append(sampled)
    print('Likes:', 'N='+str(len(likes_df.index)), 'n='+str(n))

    os.makedirs('csv/evaluation', exist_ok=True)

    # Write all samples to file
    result = pd.concat(sampled_dfs, axis=0, ignore_index=True)
    result['uid'] = result.index
    result.to_csv('csv/evaluation/samples.csv', index=False)

    # Write random samples to file
    random = result.sample(frac=1)
    random.to_csv('csv/evaluation/random.csv', index=False)
