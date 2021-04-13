#!/usr/bin/env python
# filesampler.py

import random
import argparse
import os


BYTES_TO_SAMPLE = 10000000
MBYTES_TO_SAMPLE = BYTES_TO_SAMPLE / 100000


'''
Parse command-line arguments.
'''
def get_args():
    parser = argparse.ArgumentParser(
        description="Sample " + str(MBYTES_TO_SAMPLE) + " MB from input file(s).")
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input file(s)')
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
        print("Sampling " + str(MBYTES_TO_SAMPLE) + " MB from " + file + "...")

        dest_name = os.path.splitext(os.path.basename(file))[-2]
        dest = 'sampled/' + dest_name + '.txt'

        if not os.path.exists('sampled/'):
            os.makedirs('sampled/')

        with open(file) as f:
            lines = [(random.random(), line) for line in f]

        lines.sort()

        with open(dest, 'w') as f:
            for _, line in lines:
                f.write(line)
                if f.tell() > 10000000:
                    break

        print("All done! The result is stored in " + dest + ".\n")
        i = i + 1
