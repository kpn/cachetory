from pytest import raises

from cachetory.backends.sync import from_url


def test_from_url_unknown_scheme() -> None:
    with raises(ValueError):
        from_url("invalid://")
