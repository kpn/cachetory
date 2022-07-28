from typing import Any, Callable, Dict, Tuple

from pytest import mark

from cachetory.decorators.shared import make_default_hashed_key, make_default_key


def _callable():
    """
    This is only used as a test target.
    """


@mark.parametrize(
    "callable_, args, kwargs, expected_key",
    [
        (_callable, (), {}, "tests.decorators.test_shared:_callable"),
        (_callable, (1, 42), {}, "tests.decorators.test_shared:_callable:1:42"),
        (_callable, (), {"foo": 42, "bar": "qux"}, "tests.decorators.test_shared:_callable:bar=qux:foo=42"),
        (
            _callable,
            (),
            {"bar": "qux", "foo": 42},
            "tests.decorators.test_shared:_callable:bar=qux:foo=42",
        ),
        (_callable, (1, 42), {"foo": "bar"}, "tests.decorators.test_shared:_callable:1:42:foo=bar"),
        (
            _callable,
            ("a:b",),
            {"foo:bar": "qux:quux"},
            "tests.decorators.test_shared:_callable:a::b:foo::bar=qux::quux",
        ),
    ],
)
def test_make_default_key(
    callable_: Callable[..., Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    expected_key: str,
):
    assert make_default_key(callable_, *args, **kwargs) == expected_key


def test_make_default_hashed_key():
    """
    ``make_default_hashed_key`` calls ``make_default_key`` under the hood,
    thus one smoke test is enough.
    """
    assert (
        make_default_hashed_key(_callable, "a:b", foo="bar")
        == "dc3305eaf5bc29bc29d70c3dbf7676c49bfd552cfbec17106fdf71cc01d176c9"
    )
