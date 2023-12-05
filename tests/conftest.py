from typing import Any


def pytest_addoption(parser: Any) -> None:  # noqa: ANN001
    parser.addoption(
        "--test-redis",
        action="store_true",
        dest="test_redis",
        default=False,
        help="test Redis backends",
    )
