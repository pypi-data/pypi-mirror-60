from zuper_ipce_tests.test_utils import assert_type_roundtrip
from zuper_typing.literal import make_Literal


def test_lit1():
    T = make_Literal(1)

    assert_type_roundtrip(T)
