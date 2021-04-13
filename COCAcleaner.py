#!/usr/bin/env python
# COCAcleaner.py

import argparse
import nltk
import re
import os


def clean_html(html):
    """	
    Adapted from NLTK package.	
    Removes HTML markup from the given string.
    Removes COCA article titles and parenthetical asides.
        input: the HTML string to be cleaned (string)
        output: string
    """

    # Remove inline JavaScript/CSS:	
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())	
    # Then we remove html comments. This has to be done before removing regular	
    # tags since comments can contain '>' characters.	
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)	
    # Next we can remove the remaining tags:	
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)

    # Remove article headers
    cleaned = re.sub(r'##[0-9]+ ', "", cleaned)		

    # Remove content of parentheticals
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)

    # Remove html image data
    cleaned = re.sub(r'alt=.* src=.*.', "", cleaned)

    # Remove speaker titles in spoken text
    cleaned = re.sub(r'@![^\s]*', "", cleaned)

    # Remove special characters and titles:	
    cleaned = re.sub(r"[!@##$$%^&*():\"]", "", cleaned)	
    cleaned = re.sub(r"%&%.*%&%", "", cleaned)
    cleaned = re.sub(r"//", "", cleaned)

    # Normalize 2 > whitespace to 1 whitespace
    cleaned = re.sub("\s{2,}", " ",cleaned)

    return cleaned.strip()


'''
Parse command-line arguments.
'''
def get_args():
    parser = argparse.ArgumentParser(description='Preprocess COCA file(s).')
    parser.add_argument('input_files', nargs='+', type=str,
                        help='path to input COCA file(s)')
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
        print("Cleaning " + file + "...")

        dest_name = os.path.basename(file)

        if not os.path.exists('cleaned/'):
            os.makedirs('cleaned/')
        dest = 'cleaned/' + dest_name

        outfile = open(dest, "w", encoding='utf-8')
        with open(file, encoding='utf-8') as f:
            for line in f:
                cleaned = clean_html(line)
                for sent in nltk.sent_tokenize(cleaned):
                    sent_len = len(sent.split())
                    if sent_len > 3 and sent_len < 300:
                        outfile.write(sent)
                        outfile.write("\n")

        outfile.close()

        print("All done! The result is stored in " + dest + ".\n")
        i = i + 1
