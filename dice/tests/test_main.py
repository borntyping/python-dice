from __future__ import absolute_import

from dice import main

from py.test import mark

@mark.xfail
def test_main():
    assert main("2d6") is not None
