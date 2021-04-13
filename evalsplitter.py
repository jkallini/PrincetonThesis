#!/usr/bin/env python
# evalsplitter.py

import pandas as pd
import numpy as np
import os

import argparse


def get_args():
    '''
    Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Split given csv into several csvs.')
    parser.add_argument('input_file', type=str, help='path to input csv file')
    parser.add_argument('num_splits', type=int, help='number of splits')
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Main function.
    '''

    args = get_args()

    df = pd.read_csv(args.input_file, index_col=None, header=0)
    df = df.reset_index(drop=True)

    os.makedirs('csv/evaluation/splits/', exist_ok=True)

    # Produce splits for samples
    i = 1
    for split in np.array_split(df, args.num_splits):
        split.to_csv('csv/evaluation/splits/samples_' +
                     "{:02d}".format(i) + '.csv', index=False)
        i += 1