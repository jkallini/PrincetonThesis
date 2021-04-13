#!/usr/bin/env python
# linecounter.py
# Programmatically counts the number of lines in a file.


def _make_gen(reader):
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024*1024)


'''
Get number of lines in filename.
'''
def rawgencount(filename):
    f = open(filename, 'rb')
    f_gen = _make_gen(f.raw.read)
    return sum(buf.count(b'\n') for buf in f_gen)