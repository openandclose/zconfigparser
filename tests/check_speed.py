#!/usr/bin/env python

"""compare speeds of configparser and zconfigparser.

inifile1: 100 sections (no inheritance)
inifile2: 200 sections (half of which are inheritance sections)
inifile3: tosixinch sample file ('site.sample.ini')

check_speed.py [-v| --verbose]:
    check by all inifiles (with 'verbose' or not)
check_speed.py PARSER, INIFILE, OPTION, NUMBER
    check a specific setting
    cf. 'check_speed zconfigparser inifile3 select 100'
check_speed.py build
    build inifile 1 and 2
    the repository already includes built files"""


import collections
import configparser
import cProfile
import io
import os
import pstats
import random
import re
import sys

import tosixinch.main as tmain
import zconfigparser


cdir = os.path.dirname(__file__)
inifile1 = os.path.join(cdir, 'sample1.ini')
inifile2 = os.path.join(cdir, 'sample2.ini')

# 'tsi' is short for 'tosixinch'
tsi_dir = os.path.dirname(tmain.__file__)
inifile3 = os.path.join(tsi_dir, 'data', 'site.sample.ini')


def check(parser, inifile, option, num):
    if inifile == 'inifile1':
        inifile = inifile1
    elif inifile == 'inifile2':
        inifile = inifile2
    elif inifile == 'inifile3':
        inifile = inifile3

    if parser in ('c', 'configparser'):
        config = configparser.ConfigParser()
        config.read(inifile)
        sections = config.sections()
    elif parser in ('z', 'zconfigparser'):
        config = zconfigparser.ZConfigParser()
        config.read(inifile)
        sections = config.zsections()

    # print(len(sections))
    for section in list(sections) * int(num):
        value = config.get(section, option, fallback='')


# 'rprint' is short for 'return value print'
def rprint(c, z, fname, verbose):
    def seconds(c):
        m = re.search(r'in ([0-9.]+) seconds', c)
        if m:
            return m.group(1)
        raise ValueError("The result of 'cProfile.Profile()' seems strange.")

    if verbose:
        print(c)
        print(z)
    else:
        csec = seconds(c)
        zsec = seconds(z)
        rate = str(round(float(zsec)/float(csec), 2))
        s = '%s: *%s (c:%s seconds, z:%s seconds)' % (fname, rate, csec, zsec)
        print(s)


def check_all(verbose=False):
    c = run(check, 'c', inifile1, 'bbb', 100)
    z = run(check, 'z', inifile1, 'bbb', 100)
    rprint(c, z, 'inifile1', verbose)
    c = run(check, 'c', inifile2, 'bbb', 100)
    z = run(check, 'z', inifile2, 'bbb', 100)
    rprint(c, z, 'inifile2', verbose)
    c = run(check, 'c', inifile3, 'select', 100)
    z = run(check, 'z', inifile3, 'select', 100)
    rprint(c, z, 'inifile3', verbose)
    sys.exit()


def run(func, *args):
    pr = cProfile.Profile()
    pr.enable()
    func(*args)
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    return s.getvalue()


def build_inifile():
    """make two sample ini-format files.
    'sample1.ini' has 100 sections with three options like:

    [BXQLtpEd]
    aaa=LcAyrMZR
    bbb=CAooHMUB
    ccc=zHGvkNnr

    'sample2.ini' has the same 100 sections plus 100 sections like:

    [UfjbJCDa : BXQLtpEd]
    aaa=kAcuebHs
    bbb=WmPVqHgC

    in which all sections are inherited from first 100 sections (' : ' part),
    and each only has two options.
    (half has 'aaa' and 'bbb', the other half has 'aaa' and 'ccc'.
    and the 200 sections are shuffled.

    is is meant to run only once for this test,
    and the generated files are already included in the repository.
    """

    num = 1000

    def build_random_values():
        s = []
        alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i in range(num):
            t = ''.join(random.choices(alpha, k=8))
            s.append(t)
        return s

    def build_unique_random_values():
        while True:
            s = build_random_values()
            if not len(set(s)) == num:
                continue
            break
        return s

    def build_sections():
        sections = []
        s = build_unique_random_values()
        field = ('sec', 'opt1', 'value1', 'opt2', 'value2', 'opt3', 'value3')
        Sec = collections.namedtuple('Sec', field)
        for i in range(100):
            j = i*7
            section1 = Sec(s[j+1], 'aaa', s[j+2], 'bbb', s[j+3], 'ccc', s[j+4])
            sec = s[j+5] + ' : ' + s[j+1]
            if i < 50:
                section2 = Sec(sec, 'aaa', s[j+6], 'bbb', s[j+7], '', '')
            else:
                section2 = Sec(sec, 'aaa', s[j+6], 'ccc', s[j+7], '', '')
            sections.append((section1, section2))
        return sections

    def build_section_strings(tup):
        s = ['[', tup[0], ']', '\n']
        for i in range(3):
            j = i*2
            if tup[j+1]:
                s.extend((tup[j+1], '=', tup[j+2], '\n'))
        return ''.join(s)

    def build_inifile_strings():
        ilist1 = []
        ilist2 = []
        sections = build_sections()
        for s1, s2 in sections:
            ilist1.append(build_section_strings(s1))
            ilist2.append(build_section_strings(s2))
        istr1 = ''.join(ilist1)
        ilist2.extend(ilist1)
        random.shuffle(ilist2)
        istr2 = ''.join(ilist2)
        return istr1, istr2

    def write_inifile():
        istr1, istr2 = build_inifile_strings()
        cdir = os.path.dirname(__file__)
        inifile1 = os.path.join(cdir, 'sample1.ini')
        inifile2 = os.path.join(cdir, 'sample2.ini')
        with open(inifile1, 'w') as f:
            f.write(istr1)
        with open(inifile2, 'w') as f:
            f.write(istr2)
                
    write_inifile()
    sys.exit()


def usage():
    print(__doc__)
    sys.exit()


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 1:
        check_all()
    elif len(argv) == 2:
        if argv[1] == ('-v', '--verbose'):
            check_all(verbose=True)
        elif argv[1] == 'build':
            build_inifile()
    elif len(argv) == 5:
        run(check, *argv[1:5])
        sys.exit()
    usage()


# MEMO:
# 2017/07/30
# original zconfigparser
# inifile1: *78.75 (c:0.079 seconds, z:6.221 seconds)
# inifile2: *259.49 (c:0.140 seconds, z:36.328 seconds)
# inifile3: *18.5 (c:0.010 seconds, z:0.185 seconds)


