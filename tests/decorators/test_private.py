from typing import Any, Callable, Dict, Tuple

from pytest import mark

from cachetory.decorators.private import make_key_by_default


def _callable():
    """
    This is only used as a test target.
    """


@mark.parametrize(
    "callable_, args, kwargs, expected_key",
    [
        (_callable, (), {}, "tests.decorators.test_private:_callable"),
        (_callable, (1, 42), {}, "tests.decorators.test_private:_callable:1:42"),
        (_callable, (), {"foo": 42, "bar": "qux"}, "tests.decorators.test_private:_callable:bar=qux:foo=42"),
        (
            _callable,
            (),
            {"bar": "qux", "foo": 42},
            "tests.decorators.test_private:_callable:bar=qux:foo=42",
        ),
        (_callable, (1, 42), {"foo": "bar"}, "tests.decorators.test_private:_callable:1:42:foo=bar"),
        (
            _callable,
            ("a:b",),
            {"foo:bar": "qux:quux"},
            "tests.decorators.test_private:_callable:a::b:foo::bar=qux::quux",
        ),
    ],
)
def test_make_key(
    callable_: Callable[..., Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    expected_key: str,
):
    assert make_key_by_default(callable_, *args, **kwargs) == expected_key
