#!/usr/bin/env python
# coordination.py

import sys

import spacy
from nltk import ParentedTree
from benepar.spacy_plugin import BeneparComponent

# a class to represent benepar parse trees
class BeneparTree:
    
    def __init__(self, parse_string):
        self.__tree = ParentedTree.fromstring(parse_string)

    def pretty_print(self):
        self.__tree.pretty_print(unicodelines=False)

    def __get_tree_text(self, subtree):
        return " ".join(subtree.leaves())

    def print_text(self):
        print (self.__get_tree_text(self.__tree))

    def get_simple_coordphrases(self):
        phrases = []
        for s in self.__tree.subtrees(
            lambda t: t.label() == "CC" and len(list(t.parent())) == 3):

            # Get left ad right siblings
            left = s.left_sibling()
            right = s.right_sibling()
            if left is None or right is None:
                continue
            conjunct1 = (left.label(), self.__get_tree_text(left))
            conjunct2 = (right.label(), self.__get_tree_text(right))
            conjunction = self.__get_tree_text(s)
            phrases.append((conjunct1, conjunction, conjunct2))
        return phrases


# Given an input sent, gets the parse and coordinations and
# prints the output to stdout.
def print_output(sent, display_tree=True):
    tree = BeneparTree(sent._.parse_string)
    if display_tree:
        tree.pretty_print()

    coordinations = tree.get_simple_coordphrases()
    tot = len(coordinations)
    if tot == 0:
        print("No coordination phrases found.")
    else:
        print("Found " + str(tot) + " coordination phrase(s).")

    for i in range(tot):
        print ("Coordination " + str(i+1) + ": " + str(coordinations[i]))
        i += 1


if __name__ == "__main__":

    # Load spacy model and integrate with benepar
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(BeneparComponent('benepar_en2'))

    doc = nlp("the cat and the dog")
    print("======================================================================================================================")
    print("\033[96m\033[1mReady to parse.\033[0m")
    print("Below is an example output for the phrase \"the cat and the dog\".\n")
    print("the cat and the dog")
    for sent in doc.sents:
        print_output(sent)
    print("\nEnter your sentences and phrases below.")
    print("======================================================================================================================")

    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        doc = nlp(line)
        for sent in doc.sents:
            print(sent)
            print_output(sent)