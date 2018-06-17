from datetime import datetime, timedelta
from pprint import pprint as p
import unittest

from freezegun import freeze_time
import pytest

from soros.ohlc import OHLC


@pytest.fixture(scope='module', params=[
    60, 5*60, 15*60, 30*60, 60*60, 4*60*60, 6*60*60, 12*60*60, 24*60*60])
def interval(request):
    return timedelta(minutes=request.param)


def test_no_bars(interval):
    bars = OHLC(interval)
    assert [] == bars.bars()


def test_first_bar(interval):
    bars = OHLC(interval)
    start = datetime.utcnow()
    with freeze_time(start):
        bars.on_tick(10)
        bars = bars.bars()
        assert 1 == len(bars)
        assert_bar(bars[0], 10, 10, 10, 10, start, interval)


def test_updated_bar(interval):
    bars = OHLC(interval)
    start = datetime.utcnow()
    with freeze_time(start) as time:
        bars.on_tick(10)
        time.tick()
        bars.on_tick(11)
        bars = bars.bars()
        assert 1 == len(bars)
        assert_bar(bars[0], 10, 11, 10, 11, start, interval)


def test_second_bar(interval):
    bars = OHLC(interval)
    start = datetime.utcnow()
    with freeze_time(start) as time:
        initial = datetime.utcnow()  # Hack
        bars.on_tick(10)
        time.tick(delta=interval)
        bars.on_tick(11)
        bars = bars.bars()
        assert 2 == len(bars)
        assert_bar(
            bars[1], 10, 11, 10, 11, initial + interval, interval)


def test_updated_second_bar(interval):
    bars = OHLC(interval)
    start = datetime.utcnow()
    with freeze_time(start) as time:
        initial = datetime.utcnow()  # Hack
        bars.on_tick(10)
        time.tick(delta=interval)
        bars.on_tick(11)
        time.tick()
        bars.on_tick(12)
        bars = bars.bars()
        assert 2 == len(bars)
        assert_bar(
            bars[1], 10, 12, 10, 12, initial + interval, interval)


def test_missed_bar(interval):
    bars = OHLC(interval)
    start = datetime.utcnow()
    with freeze_time(start) as time:
        initial = datetime.utcnow()  # Hack
        bars.on_tick(10)
        time.tick(delta=interval*2)
        bars.on_tick(11)
        bars = bars.bars()
        assert 3 == len(bars)
        assert_bar(
            bars[1], 10, 10, 10, 10, initial + interval, interval)
        assert_bar(
            bars[2], 10, 11, 10, 11, initial + interval*2, interval)


def test_max_bars(interval):
    bars = OHLC(interval, max_bars=3)
    start = datetime.utcnow()
    with freeze_time(start) as time:
        for _ in range(3):
            bars.on_tick(10)
            time.tick(delta=interval)
        assert 3 == len(bars.bars(n=100))
        bars.on_tick(12)
        assert 3 == len(bars.bars(n=100))
        bars.on_tick(12)
        assert 3 == len(bars.bars(n=100))


def assert_bar(bar, o, h, l, c, t, interval):
    assert bar['open'] == o
    assert bar['high'] == h
    assert bar['low'] == l
    assert bar['close'] == c
    # TODO: Make this test better.
    assert bar['start'] > (t - interval)


if __name__ == "__main__":
    unittest.main()
