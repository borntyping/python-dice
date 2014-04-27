====
dice
====

.. image:: https://pypip.in/v/dice/badge.png
    :target: https://pypi.python.org/pypi/dice
    :alt: Latest PyPI version
        
.. image:: https://travis-ci.org/borntyping/python-dice.png
    :target: https://travis-ci.org/borntyping/python-dice
    :alt: Travis-CI build status
           

A library and command line tool for parsing and evaluating dice notation.

Usage
=====

From the command line::

    roll 3d6

From python::

    import dice
    dice.roll('3d6')

Notation
========

The expression works like a simple equation parser with some extra operators.

*The following operators are listed in order of precedence.*

The dice ('d') operator takes an amount (A) and a number of sides (S), and
returns a list of A random numbers between 1 and S. For example: ``4d6`` may
return ``[6, 3, 2, 4]``.

If A is not specified, it is assumed you want to roll a single die.
``d6`` is equivalent to ``1d6``.

Basic integer operations are available: ``16 / 8 * 4 + 2 - 1 -> 9``.

A set of rolls can be turned into an integer with the total (``t``) operator.
``6d1t`` will return ``6`` instead of ``[1, 1, 1, 1, 1, 1]``. Applying
integer operations to a list of rolls will total them automatically.

A set of dice rolls can be sorted with the sort (``s``) operator. ``4d6s``
will not change the return value, but the dice will be sorted from lowest to
highest.

The lowest or highest rolls can be selected with ``^`` and ``v``. ``6d6^3``
will keep the highest 3 rolls, whereas ``6d6v3`` will select the lowest 3
rolls.

Licence
=======

The MIT License (MIT)

Copyright (c) 2013 Sam Clements

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

