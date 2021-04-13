#!/usr/bin/env python
# evaluate.py

import pandas as pd
import argparse

from colorama import init
init()

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_args():
    '''
    Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Evaluate coordination phrases in the given csv file.')
    parser.add_argument('input_file', type=str, help='path to input csv file')
    return parser.parse_args()


if __name__ == "__main__":
    '''
    Main function.
    '''
    
    args = get_args()

    df = pd.read_csv(args.input_file, index_col=None, header=0)
    dest_name = args.input_file.split('.')[0]
    tot = len(df.index)

    data = []

    for index, row in df.iterrows():
        sent = str(row['Sentence Text'])
        conj1 = str(row['1st Conjunct Text'])
        cat1 = str(row['1st Conjunct Category'])
        conj2 = str(row['2nd Conjunct Text'])
        cat2 = str(row['2nd Conjunct Category'])
        conjunction = str(row['Conjunction'])
        uid = str(row['uid'])

        conj1_labeled = color.BOLD + color.DARKCYAN + '[' + cat1 + ' ' + conj1 + ']' + color.END
        conj2_labeled = color.BOLD + color.DARKCYAN + '[' + cat2 + ' ' + conj2 + ']' + color.END

        ccp = conj1 + ' ' + conjunction + ' ' + conj2
        ccp_labeled = conj1_labeled + ' ' + conjunction + ' ' + conj2_labeled
        sent = sent.replace(ccp, ccp_labeled)

        print('(' + str(index + 1) + '/' + str(tot) + ')')
        print(sent)
        print('Coordination phrase:', ccp_labeled)

        while True:
            user_input = input(
                "Is this coordination phrase correctly labeled? (y/n)\n")
            if user_input.lower() not in ('y', 'yes', 'n', 'no'):
                print("Please answer (y/n) or (yes/no).")
                continue
            else:
                correct = False
                if user_input.lower() in ('y', 'yes'):
                    correct = True
                if user_input.lower() in ('n', 'no'):
                    correct = False
                data.append([cat1, conj1, cat2, conj2, conjunction, correct, uid])
                break

    columns = ['1st Conjunct Category', '1st Conjunct Text',
               '2nd Conjunct Category', '2nd Conjunct Text',
               'Conjunction', 'Correct?', 'uid']
    new_df = pd.DataFrame(data, columns=columns)
    new_df.reset_index(inplace=True, drop=True)

    new_df.to_csv(dest_name + '_eval.csv')

    print('All done! The result is stored in ' + dest_name + '_eval.csv.')
