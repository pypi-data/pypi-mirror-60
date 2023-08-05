from nose.tools import assert_equal, raises

from zuper_commons.types import ZValueError
from zuper_typing.get_patches_ import assert_equivalent_types
from zuper_typing.literal import get_Literal_args, is_Literal, make_Literal
from zuper_typing.subcheck import can_be_used_as2, value_liskov


@raises(ZValueError)
def test_zt_literal0a():
    """ No empty literals """
    make_Literal()


@raises(ZValueError)
def test_zt_literal0b():
    """ Only one type """
    make_Literal(1, "a")


def test_zt_literal1():
    L = make_Literal(1)
    assert is_Literal(L)
    assert_equal(get_Literal_args(L), (1,))


def test_zt_literal2():
    L1 = make_Literal(1)
    L2 = make_Literal(1)
    assert_equivalent_types(L1, L2)


def test_zt_literal3():
    L1 = make_Literal(1, 2)
    L2 = make_Literal(2, 1)
    assert_equivalent_types(L1, L2)


def test_zt_literal4():
    L1 = make_Literal(1)
    L2 = make_Literal(1)
    r = can_be_used_as2(L1, L2)
    assert r, r


def test_zt_literal5():
    L1 = make_Literal(1, 2)
    L2 = make_Literal(2, 1)
    r = can_be_used_as2(L1, L2)
    assert r, r


def test_zt_literal6():
    L1 = make_Literal(1)
    L2 = make_Literal(2, 1)
    r = can_be_used_as2(L1, L2)
    assert r, r
    r = can_be_used_as2(L2, L1)
    assert not r, r


def test_zt_literal7():
    L1 = make_Literal(1)
    T2 = int
    r = can_be_used_as2(L1, T2)
    assert r, r
    r = can_be_used_as2(T2, L1)
    assert not r, r


def test_zt_literal8():
    L1 = make_Literal(1)
    T2 = object
    r = can_be_used_as2(L1, T2)
    assert r, r
    r = can_be_used_as2(T2, L1)
    assert not r, r


def test_zt_literal9():
    L1 = make_Literal(1)
    assert value_liskov(1, L1)
    assert not value_liskov(2, L1)
