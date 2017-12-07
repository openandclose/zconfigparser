
.. vim: set spell spelllang=en_us :


Overview
========

The library provides a customized
`configparser.ConfigParser <https://docs.python.org/3/library/configparser.html#configparser-objects>`__ object,
adding just one small feature,
which seems to have originated from ``zend config`` (A web framework).

It processes special ``ZSEP`` string in sections (default: ``' : '``).
So that the section ``[aa : bb]`` means ``[aa]``,
but now ``[aa]`` has a parent section ``[bb]``.

It is useful in omitting duplicate options in related or similar sections.

(Only for ``'dot separator'``, reverse ordering is also supported,
e.g. ``[bb.aa]``. See `below <#dot-separator>`__)

Installation
------------

It is a single file Python module, with no other library dependency.

Only **Python 3.5 and above** are supported.::

    pip install zconfigparser

.. note ::

    It is mainly developed for `my other script <https://github.com/openandclose/tosixinch>`__.

    And it is meant to be an user-level script helper.

Usage
-----

.. code:: python

    ## myconfig.ini
    [aa : bb]
    x=aaa
    [bb]
    x=bbb
    y=bbb

    >>>from zconfigparser import ZConfigParser
    >>>config = ZConfigParser()
    >>>config.read('myconfig.ini')
    >>>config.get('aa : bb', 'x')
    aaa
    >>>config.get('aa', 'x')
    aaa
    >>>config.get('aa', 'y')
    bbb

* ``[aa]`` doesn't have ``y`` option,
  so the option in ``[bb]`` is looked-up instead (if any).

* In ``.get``, both section names ``[aa]`` and ``[aa : bb]`` can be used.
  They are called
  ``short [section] name`` and ``long [section] name`` respectively.

* the original ``Configparser`` values are preserved in item accesses
  e.g. ``config['aa : bb']['x']``.
  (So only ``long name`` can be used there).


Specification
-------------

Changed Function
^^^^^^^^^^^^^^^^

``.get(section, key, *, raw=False, vars=None[, fallback])``
    Explained above. It overrides ``Configparser``'s ``.get``.
    Signature is the same.

Added Functions
^^^^^^^^^^^^^^^

``.has_zsection(section)``
    Return True or False, according to the existence of a section,
    as ZConfigParser sees it. Accept ``long names`` and ``short names``.

    So using above example::

        >>> config.has_zsection('aa : bb')
        True
        >>> config.has_zsection('aa')
        True

    Note ``Configparser``'s ``.has_section`` is kept as is. ::

        >>> config.has_section('aa : bb')
        True
        >>> config.has_section('aa')
        False

``.has_zoption(section, option)``
    Return True or False, according to the existence of a option,
    as ZConfigParser sees it. Accept ``long names`` and ``short names``.

    Note ``Configparser``'s ``.has_option`` is kept as is. ::

        >>> config.has_zoption('aa : bb', 'x')
        True
        >>> config.has_option('aa : bb', 'y')
        False

``.zsections()``
    Return a set containing all short section names in config.
    Accept ``long names`` and ``short names``.

    It also does error checks config-wide. See `below <#errors>`__

Added Argument
^^^^^^^^^^^^^^

``ZSEP``
    Default separator word is ``' : '``,
    exactly one space before and after ``':'``.
    To change this, use the argument.

.. code:: python

    config = ZConfigParser(ZSEP='->')   # separator is '->'.

Lookup Order:
^^^^^^^^^^^^^

Lookup order is depth-first.

.. code:: python

    ## myconfig.ini
    [aa : bb : cc]
    [bb : dd]
    [cc : ee]
    x=ccc
    [dd]
    x=ddd
    [ee]
    x=eee

    >>>config.get('aa', 'x')
    ddd                     ## order: aa -> bb -> dd -> cc -> ee

dot separator:
^^^^^^^^^^^^^^

Some examples are found using a 'dot' for separator, reversing inheritance
order. And indeed it seems natural in this case.

So although a little confusing, it is also implemented here.
Note it is a special case only when ``ZSEP='.'``. ::

    [aa : bb : cc] ('cc' is grandparent)
       -->  -->

    [aa.bb.cc]('aa' is grandparent) 
      <-- <--

Errors:
^^^^^^^

Errors are rather rigid.
Before looking into whether or not there are actual conflicts in *options*,
it just checks *sections structure*, and judges accordingly.
It is regardless of ``Configparser`` setting of ``'strict'``.

* **Parent section lookup failure** raises
  ``zconfigparser.NoZSectionError``.
  (When there is ``[aa : bb]``,
  there must be ``[bb]`` or ``[bb : xx]`` etc.)

* **Blank parent section** also raises ``zconfigparser.NoZSectionError``.
  (``[aa : ]`` etc.)

* **More than two same leftmost section names** raise
  ``zconfigparser.DuplicateZKeyError``.
  (cf. any two combination of ``[aa]``, ``[aa : bb]``, ``[aa : cc]``)

* **Circular lookup** raises ``zconfigParser.RecursiveZkeyError``
  (``[aa : bb]``, ``[bb : cc]``, ``[cc : aa]``)

Note that ``ZConfigParser`` does not automatically check
``Parent section lookup failure``.
``Configparser`` can read multiple config files or strings,
so deciding an appropriate time for validation is rather difficult.

* ``.get`` detects ``Parent section lookup failure``
  only for *parsed* sections.

* ``.zsections`` checks it for all sections,
  because it parses all sections.
  So, it can be used for manual config-wide validation.

And it raises ``zconfigparser.NoZOptionError``,
when nonexistent option is looked-up
and default or fallback is not provided.


Thanks to
---------

Mr. Kazzer's
`nestedconfigparser <https://github.com/Kazzer/nestedconfigparser>`__.
The idea of overriding ``._unify_values`` is from his code.
I think this is a very clean approach.
