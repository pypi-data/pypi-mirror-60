import pytest

from hypothesis import given, example
from hypothesis import strategies as st

import jigu.error
from jigu.core import Coin, Dec

from jigu.core.denoms import *


@pytest.fixture
def d1():
    return uLuna


@pytest.fixture
def d2():
    return uKRW


def test_make_coin(d1):
    coin = Coin(d1, "13929")
    assert coin.denom == d1
    assert coin.amount == 13929

    coin = Coin(d1, "0.006250000000000000")
    assert coin.denom == d1
    assert coin.amount == Dec("0.00625")


@given(x=st.integers())
def test_coin_amount_type(x, d1):

    # should not be different with integers
    coin = Coin(d1, x)
    coin2 = Coin(d1, str(x))
    assert coin.amount == coin2.amount


@given(x=st.integers())
def test_coin_eq(x, d1, d2):
    # both denom and amount
    coin = Coin(d1, x)
    coin2 = Coin(d1, x)
    assert coin == coin2

    # denoms different
    coin3 = Coin(d1, x)
    coin4 = Coin(d2, x)
    assert coin3 != coin4

    # amount different
    coin5 = Coin(d1, 4)
    coin6 = Coin(d1, 8)
    assert coin5 != coin6

    # amount type different
    coin7 = Coin(d1, 4)
    with pytest.warns(SyntaxWarning):  # should get converted to integer
        coin8 = Coin(d1, 4.2)
        assert coin7 == coin8
    coin9 = Coin(d1, "4.2")
    assert coin7 != coin9


@given(x=st.integers(), y=st.integers())
def test_coin_add(x, y, d1, d2):

    coin = Coin(d1, x)
    coin2 = Coin(d1, y)
    assert (coin + coin2) == Coin(d1, x + y)

    with pytest.raises(Coin.DenomIncompatibleError):
        coin3 = Coin(d1, x)
        coin4 = Coin(d2, y)
        coin3 + coin4


@given(x=st.integers(), y=st.integers())
def test_coin_sub(x, y, d1, d2):
    coin = Coin(d1, x)
    coin2 = Coin(d1, y)
    assert (coin - coin2) == Coin(d1, x - y)

    with pytest.raises(Coin.DenomIncompatibleError):
        coin3 = Coin(d1, x)
        coin4 = Coin(d2, y)
        coin3 - coin4


def test_coin_compare(d1, d2):
    coin = Coin(d1, 0)
    coin2 = Coin(d1, 1)
    coin3 = Coin(d2, 0)
    coin4 = Coin(d2, 1)

    coin_dup = Coin(d1, 0)

    assert coin < coin2
    assert coin2 > coin

    assert coin >= coin_dup
    assert coin <= coin_dup

    with pytest.raises(Coin.DenomIncompatibleError):
        coin < coin3
