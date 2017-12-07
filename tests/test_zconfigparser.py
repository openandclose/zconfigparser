
import pytest

import zconfigparser

ZConfigParser = zconfigparser.ZConfigParser


def getconfs(s):
    conf = ZConfigParser()
    conf.read_string(s)
    return conf

## ------------------------------------------------------------------
def test_get1():
    s = '''
    [aa]
    x=aaa'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'aaa'
def test_get2():
    s = '''
    [aa : bb]
    [bb]
    x=bbb'''
    confs = getconfs(s)
    assert confs.get('aa : bb', 'x') == 'bbb'
def test_get3():
    s = '''
    [aa : bb]
    [bb]
    x=bbb'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'bbb'
def test_get4():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    x=ccc'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'ccc'

## ------------------------------------------------------------------
def test_nosec1():
    # Even when possible to get value, raises no section error.
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : dd]
    x=ccc'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.NoZSectionError):
        assert confs.get('aa', 'x') == 'ccc'
def test_nosec2():
    # Even when possible to get value, 
    # and concerned sections are valid ('cc', 'dd'), raises no section error.
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : dd]
    x=ccc
    [dd : ee]
    x=ddd'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.NoZSectionError):
        assert confs.get('aa', 'x') == 'ccc'

## ------------------------------------------------------------------
def test_recursion():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : aa]
    x=ccc'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.RecursiveZkeyError):
        assert confs.get('aa', 'x') == 'ccc'
def test_recursion_default():
    s = '''
    [DEFAULT]
    x=xxx
    [aa : bb]
    [bb : cc]
    [cc : aa]'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.RecursiveZkeyError):
        assert confs.get('aa', 'x') == 'xxx'
def test_recursion_nooption():
    # section search is first,
    # so recursive section error before no option error.
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : dd]
    [dd : aa]'''
    confs = getconfs(s)
    # with pytest.raises(zconfigparser.NoZOptionError):
    with pytest.raises(zconfigparser.RecursiveZkeyError):
        assert confs.get('aa', 'x') == 'xxx'

## ------------------------------------------------------------------
def test_duplicate():
    # duplicate keys error is from `zdict`, not from `ZConfigParser`.
    # because otherwise the code would get complex,
    # wrapping `ConfigParser.DuplicateSectionError`, etc..
    s = '''
    [aa : bb]
    [aa : cc]
    x=aaa'''
    with pytest.raises(zconfigparser.DuplicateZKeyError):
        confs = getconfs(s)
        assert confs.get('aa', 'x') == 'aaa'
def test_duplicate_recurcive():
    # duplicate keys error is from `zdict.__setitem__`,
    # it is before recursive keys error,
    # which is detected when getting keys.
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : aa]
    [aa : cc]
    x=aaa'''
    with pytest.raises(zconfigparser.DuplicateZKeyError):
        confs = getconfs(s)
        assert confs.get('aa', 'x') == 'aaa'

## ------------------------------------------------------------------
def test_blank1():
    s = '''
    [aa : ]
    x=aaa'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.NoZSectionError):
        assert confs.get('aa', 'x') == 'aaa'
def test_blank2():
    s = '''
    [aa :  ]
    x=aaa'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.NoZSectionError):
        assert confs.get('aa', 'x') == 'aaa'
def test_blank3():
    s = '''
    [ : aa]
    x=aaa'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.NoZSectionError):
        assert confs.get('aa', 'x') == 'aaa'
def test_blank2():
    s = '''
    [  : aa]
    x=aaa'''
    confs = getconfs(s)
    with pytest.raises(zconfigparser.NoZSectionError):
        assert confs.get('aa', 'x') == 'aaa'

## ------------------------------------------------------------------
def test_zsections():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : dd]
    [dd]
    x=ddd'''
    confs = getconfs(s)
    assert confs.zsections() == {
            'aa', 'bb', 'cc', 'dd', 'aa : bb', 'bb : cc', 'cc : dd'}
def test_zsections_duplicate():
    # `zsections()` is just a `keys()` lookup, not detecting Errors.
    # but after setting keys, which might raise duplicate keys errors.
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    [bb : dd]
    x=ccc'''
    with pytest.raises(zconfigparser.DuplicateZKeyError):
        confs = getconfs(s)
        assert confs.zsections() == {
                'aa', 'bb', 'cc', 'dd', 'aa : bb', 'bb : cc', 'bb : dd'}
def test_zsections_recursive():
    # `zsections()` is just a `keys()` lookup, not detecting Errors.
    s = '''
    [aa : bb]
    [bb : cc]
    [cc : aa]
    x=ccc'''
    confs = getconfs(s)
    # with pytest.raises(zconfigparser.RecursiveZkeyError):
    assert confs.zsections() == {
            'aa', 'bb', 'cc', 'aa : bb', 'bb : cc', 'cc : aa'}
def test_zsections_nosection():
    # `zsections()` is just a `keys()` lookup, not detecting Errors.
    s = '''
    [aa : bb]
    [bb : cc]
    x=bbb'''
    confs = getconfs(s)
    # with pytest.raises(zconfigparser.NoZSectionError):
    assert confs.zsections() == {
            'aa', 'bb', 'aa : bb', 'bb : cc'}

## ------------------------------------------------------------------
def test_has_zsection():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    x=ccc'''
    confs = getconfs(s)
    assert confs.has_zsection('bb') == True
def test_has_zsection2():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    x=ccc'''
    confs = getconfs(s)
    assert confs.has_zsection('ss') == False

## ------------------------------------------------------------------
def test_has_zoption():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    x=ccc'''
    confs = getconfs(s)
    assert confs.has_zoption('aa : bb', 'x') == True
def test_has_zoption2():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    x=ccc'''
    confs = getconfs(s)
    assert confs.has_zoption('aa', 'x') == True
def test_has_zoption3():
    s = '''
    [aa : bb]
    [bb : cc]
    [cc]
    x=ccc'''
    confs = getconfs(s)
    assert confs.has_zoption('ss', 'x') == False

## ------------------------------------------------------------------
def test_get_complex():
    s = '''
    [aa : bb : cc]
    [bb : dd]
    [cc : ee]
    x=ccc
    [dd]
    x=ddd
    [ee]
    x=eee'''
    confs = getconfs(s)
    assert confs.get('aa', 'x') == 'ddd'
    assert confs._sections._get_shortnames('aa') == [
            'aa', 'bb', 'dd', 'cc', 'ee']

## ------------------------------------------------------------------
def test_default():
    s = '''
    [DEFAULT]
    x=ddd
    y=ddd
    [aa : bb]
    x=aaa
    [bb]
    x=bbb'''
    confs = getconfs(s)
    assert confs.get('aa', 'y') == 'ddd'
    assert confs.get('DEFAULT', 'x') == 'ddd'
