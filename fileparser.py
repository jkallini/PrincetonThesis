#!/usr/bin/env python
# fileparser.py
# Load the text file(s) passed as command-line argument(s). Parse each
# sentence in the file using the Berkeley parser. Write each sentence
# parse tree to a csv file. If the input is named 'sample.txt' (or
# '/data/sample.txt', or the input is in any number of nested
# subdirectories), the result is written to '/csv/sample/sample.csv'.

from sys import stderr
import spacy
from benepar.spacy_plugin import BeneparComponent

import pandas as pd

import argparse
import os

from tqdm import tqdm
from linecounter import rawgencount


'''
Parse command-line arguments.
'''
def get_args():
    parser = argparse.ArgumentParser(
        description='Generate parse tree for each line of the cleaned input file(s).')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input file(s)')
    return parser.parse_args()


'''
Main function.
'''
if __name__ == "__main__":

    args = get_args()

    # Load spacy model
    print("Loading spaCy's large English model...")
    nlp = spacy.load("en_core_web_lg")

    # Integrate with benepar
    print("Integrating spaCy model with Benepar...")
    print("You may ignore any messages about TensorFlow not being optimized.")
    nlp.add_pipe(BeneparComponent('benepar_en2'))
    print()

    i = 1
    tot = str(len(args.input_files))

    input_files = reversed(args.input_files)

    for file in input_files:

        data = []
        num_lines = rawgencount(file)

        print("(" + str(i) + "/" + tot + ")")
        print("Beginning parse of " + file
              + "! If the input file is large, this may take a few hours...")
        with open(file, encoding='utf-8') as f:
            for line in tqdm(f, total=num_lines):
                try:
                    doc = nlp(line)
                    for sent in doc.sents:
                        data.append([sent.string.strip(), sent._.parse_string])
                except Exception as e:
                    print(str(e), file=stderr)

        columns = ['Sentence Text', 'Sentence Parse Tree']
        df = pd.DataFrame(data, columns=columns)

        dest_name = os.path.splitext(os.path.basename(file))[-2]
        dest_dir = 'csv/' + dest_name

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        df.to_csv(dest_dir + '/' + dest_name + '.csv', index=False)

        print("All done! The result is stored in " +
              dest_dir + '/' + dest_name + '.csv.\n')
        i = i + 1
