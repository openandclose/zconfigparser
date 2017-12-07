#!/usr/bin/env python
# -*- coding: utf_8 -*-

## it is not test.
## just checking configparser sepecification details.


import pytest
import configparser
import io

def getconfs(s):
    conf = configparser.ConfigParser()
    conf.read_string(s)
    return conf

def getconfs_nonstrict(s):
    # the same as getconfs, except `strict=False`
    conf_ns = configparser.ConfigParser(strict=False)
    conf_ns.read_string(s)
    return conf_ns

def getconfs_init_default(s, t):
    # the same as getconfs, except initial default dict
    conf = configparser.ConfigParser(t)
    conf.read_string(s)
    return conf


## ------------------------------------------------------------------
# dulicate sections: successive reading overwrites sections 
#   whether `strict` is True or False.
def test_dupli():
    s = '''
    [aa]
    x=aaa
    [bb]
    x=bbb
    [aa]
    x=ccc'''
    with pytest.raises(configparser.DuplicateSectionError):
        confs = getconfs(s)

    # strict=False
    confs_ns = getconfs_nonstrict(s)
    assert confs_ns.get('aa', 'x') == 'ccc'

def test_dupli_read_two_times():
    s = '''
    [aa]
    x=aaa
    [bb]
    x=bbb'''
    t = '''
    [cc]
    x=ccc
    [aa]
    x=ddd'''
    confs = getconfs(s)
    confs.read_string(t)
    assert confs.get('aa', 'x') == 'ddd'

    # strict=False
    confs_ns = getconfs_nonstrict(s)
    confs_ns.read_string(t)
    assert confs_ns.get('aa', 'x') == 'ddd'


## ------------------------------------------------------------------
# 'Values can span multiple lines, 
#   as long as they are indented deeper' ( in doc and source )

def test_indent():
    s = '''
    [aa]
    x = aaa
        aaa'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'aaa\naaa'

    s = '''
    [aa]
    x = aaa
      aaa'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'aaa\naaa'

    s = '''
    [aa]
    x = aaa
     aaa'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'aaa\naaa'

    s = '''
    [aa]
    x = aaa
    aaa'''
    with pytest.raises(configparser.ParsingError):
        confs = getconfs(s)
        assert confs.get('aa', 'x') == 'aaa\naaa'

def test_indent_newline():
    s = '''
    [aa]
    x =
      aaa'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == '\naaa'

    s = '''
    [aa]
    x =
     aaa'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == '\naaa'

    s = '''
    [aa]
    x =
    aaa'''
    with pytest.raises(configparser.ParsingError):
        confs = getconfs(s)
        assert confs.get('aa', 'x') == '\naaa'


## ------------------------------------------------------------------
# Document unclear
# [ ] is OK, and different from [  ](two spaces), but [](no space) is Error.

def test_blanks():
    s = '''
    [ ]
    x = aaa'''
    confs = getconfs(s)
    assert confs.get(' ', 'x') == 'aaa'

def test_blanks2():
    s = '''
    [ ]
    x = aaa
    [  ]
    x = bbb'''
    confs = getconfs(s)
    assert confs.get(' ', 'x') == 'aaa'
    assert confs.get('  ', 'x') == 'bbb'

def test_blanks3():
    s = '''
    []
    x = aaa'''
    with pytest.raises(configparser.MissingSectionHeaderError):
        confs = getconfs(s)
        assert confs.get('', 'x') == 'aaa'


## ------------------------------------------------------------------
# just confirming whether `.write` is OK.
def test_write():
    s = '''[DEFAULT]
x = ddd
y = ddd

[aa]
x = aaa

'''
    confs = getconfs(s)
    output = io.StringIO()
    confs.write(output)
    # print(output.getvalue())
    assert output.getvalue() == s


## ------------------------------------------------------------------
# just confirming both 'initial default' and file with DEFAULT section.
def test_with_default_init():
    t = {'x': 'ddd', 'y':'ddd'}
    s = '''
    [DEFAULT]
    x = eee
    y = eee
    [aa]
    x = aaa'''
    confs = getconfs_init_default(s, t)
    assert confs.get('DEFAULT', 'y') == 'eee'
    assert confs.get('aa', 'y') == 'eee'
