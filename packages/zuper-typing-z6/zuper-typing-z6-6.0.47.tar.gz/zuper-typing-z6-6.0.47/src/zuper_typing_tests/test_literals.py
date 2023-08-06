from typing import Tuple


from . import logger
from typing_extensions import Literal

from zuper_typing.my_dict import make_CustomTuple
from zuper_typing.subcheck import value_liskov


def test_literals1():
    T = Tuple[Literal["string"], str]
    v = ("string", "my string")
    can = value_liskov(v, T)
    assert can, can


def test_literals2():
    T = Tuple[Literal["string"], str]
    v = ("not the string", "my string")
    can = value_liskov(v, T)
    assert not can, can


def test_literals3():
    T = Tuple[Literal["string"], str]
    v = ("string", 42)
    can = value_liskov(v, T)
    assert not can, can


def test_tuple_making():
    # from zuper_ipcl.debug_print_ import debug_print
    from zuper_typing import dataclass

    @dataclass
    class A:
        a: int

    logger.info(aa=A, a=A(1), b=A(1), c=A(2))
    T1 = make_CustomTuple((Literal["string"], str))
    T2 = make_CustomTuple((Literal["integer"], int))

    logger.info(T1=T1, T2=T2)
