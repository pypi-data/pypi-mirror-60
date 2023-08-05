from typing import Tuple, Union

from typing_extensions import Literal

from zuper_ipce_tests.test_utils import assert_object_roundtrip
from zuper_typing import dataclass
from zuper_typing.subcheck import value_liskov


def test_ipce_union1():
    @dataclass
    class A:
        t: Union[Tuple[Literal["string"], str], Tuple[Literal["integer"], int]]

    objects = [
        A(("string", "my string")),
        A(("integer", 42)),
    ]

    for ob in objects:
        can = value_liskov(ob, A)
        assert can, can
        assert_object_roundtrip(ob)
