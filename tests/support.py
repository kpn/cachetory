from pytest import mark

if_redis_enabled = mark.skipif("not config.getoption('test_redis')")
