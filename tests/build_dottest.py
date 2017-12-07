#!/usr/bin/env python

"""
make dot separator test file from ordinary test file.

(from `test_zconfigparser.py` to `test_zconfigparser_dot.py`)
"""

import os
import re
import sys

TESSDIR = os.path.dirname(__file__)
fromfile = os.path.join(TESSDIR, 'test_zconfigparser.py')
tofile = os.path.join(TESSDIR, 'test_zconfigparser_dot.py')

if os.path.getmtime(tofile) > os.path.getmtime(fromfile):
    print('already built')
    sys.exit()

with open(fromfile) as f:
    lines = f.read()

INIT = r'conf = ZConfigParser\(\)'
DOTINIT = r"conf = ZConfigParser(ZSEP='.')"
INIT = r'(w*)%s\n' % INIT
DOTINIT = r'\1%s\n' % DOTINIT
lines = re.sub(INIT, DOTINIT, lines)

# presuppose no intermediate newlines ('\n') in section names.
lines = re.sub(r'(\w+) : (\w+) : (\w+) : (\w+)', r'\4.\3.\2.\1', lines)
lines = re.sub(r'(\w+) : (\w+) : (\w+)', r'\3.\2.\1', lines)
lines = re.sub(r'(\w+) : (\w+)', r'\2.\1', lines)
lines = re.sub(r'(\w+) : (|\s+)', r'\2.\1', lines)
lines = re.sub(r'(|\s+) : (\w+)', r'\2.\1', lines)

with open(tofile, 'w') as f:
    f.write(lines)
