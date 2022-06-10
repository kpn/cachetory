def pytest_addoption(parser):
    parser.addoption(
        "--test-redis",
        action="store_true",
        dest="test_redis",
        default=False,
        help="test Redis backends",
    )
