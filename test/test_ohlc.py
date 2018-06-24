from datetime import datetime, timedelta
from pprint import pprint as p
import unittest
from unittest.mock import Mock, call

from freezegun import freeze_time
import pytest

from soros import ohlc
from soros.constants import*
from soros.ohlc import OHLC


@pytest.fixture(scope='module', params=[
    60, 5*60, 15*60, 30*60, 60*60, 4*60*60, 6*60*60, 12*60*60, 24*60*60])
def interval(request):
    return timedelta(seconds=request.param)


def assert_bar(bar, o, h, l, c, t, interval):
    assert bar['open'] == o
    assert bar['high'] == h
    assert bar['low'] == l
    assert bar['close'] == c
    # TODO: Make this test better.
    assert bar['start'] > (t - interval)


def test_no_bars(interval):
    bars = OHLC('exchange', 'symbol', interval)
    assert [] == bars.bars()


def test_first_bar(interval):
    bars = OHLC('exchange', 'symbol', interval)
    start = datetime.utcnow()
    with freeze_time(start):
        bars.on_tick(10)
        bars = bars.bars()
        assert 1 == len(bars)
        assert_bar(bars[0], 10, 10, 10, 10, start, interval)


def test_updated_bar(interval):
    bars = OHLC('exchange', 'symbol', interval)
    start = datetime.utcnow()
    with freeze_time(start) as time:
        bars.on_tick(10)
        time.tick()
        bars.on_tick(11)
        bars = bars.bars()
        assert 1 == len(bars)
        assert_bar(bars[0], 10, 11, 10, 11, start, interval)


def test_second_bar(interval):
    bars = OHLC('exchange', 'symbol', interval)
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
    bars = OHLC('exchange', 'symbol', interval)
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
    bars = OHLC('exchange', 'symbol', interval)
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
    bars = OHLC('exchange', 'symbol', interval, max_bars=3)
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


def test_bar_first_events(monkeypatch):
    interval = timedelta(seconds=60)
    bars = OHLC('exchange', 'symbol', interval)

    start_time = datetime(
        year=2012,
        month=1,
        day=1,
        hour=12,
        minute=30,
        second=10)
    with freeze_time(start_time) as time:
        mock_hub = Mock()
        monkeypatch.setattr(ohlc, 'hub', mock_hub)
        bars.on_tick(10)

        key = "{}:{}:{}:{}".format(
            UPDATED_BAR,
            'exchange',
            'symbol',
            int(interval.total_seconds()))
        bar = {
            'open': 10,
            'high': 10,
            'low': 10,
            'close': 10,
            'start': datetime(
                year=2012,
                month=1,
                day=1,
                hour=12,
                minute=30,
                second=0)
        }
    mock_hub.publish.assert_called_once_with(key, bar)


def test_updated_bar_event(monkeypatch):
    interval = timedelta(seconds=60)
    bars = OHLC('exchange', 'symbol', interval)

    start_time = datetime(
        year=2012,
        month=1,
        day=1,
        hour=12,
        minute=30,
        second=10)
    with freeze_time(start_time) as time:
        mock_hub = Mock()
        monkeypatch.setattr(ohlc, 'hub', mock_hub)
        bars.on_tick(10)
        key = "{}:{}:{}:{}".format(
            UPDATED_BAR,
            'exchange',
            'symbol',
            int(interval.total_seconds()))
        bar = {
        'open': 10,
        'high': 10,
        'low': 10,
        'close': 10,
        'start': datetime(
            year=2012,
            month=1,
            day=1,
            hour=12,
            minute=30,
            second=0)
        }
        mock_hub.publish.assert_called_once_with(key, bar)

        time.tick(timedelta(seconds=1))
        bars.on_tick(11)
        key = "{}:{}:{}:{}".format(
            UPDATED_BAR,
            'exchange',
            'symbol',
            int(interval.total_seconds()))
        bar = {
            'open': 10,
            'high': 11,
            'low': 10,
            'close': 11,
            'start': datetime(
                year=2012,
                month=1,
                day=1,
                hour=12,
                minute=30,
                second=0)
        }
    assert mock_hub.publish.call_count == 2
    mock_hub.publish.assert_any_call(key, bar)


def test_complete_bar_event(monkeypatch):
    interval = timedelta(seconds=60)
    bars = OHLC('exchange', 'symbol', interval)

    start_time = datetime(
        year=2012,
        month=1,
        day=1,
        hour=12,
        minute=30,
        second=10)
    with freeze_time(start_time) as time:
        mock_hub = Mock()
        monkeypatch.setattr(ohlc, 'hub', mock_hub)
        bars.on_tick(10)
        key = "{}:{}:{}:{}".format(
            UPDATED_BAR,
            'exchange',
            'symbol',
            int(interval.total_seconds()))
        bar = {
        'open': 10,
        'high': 10,
        'low': 10,
        'close': 10,
        'start': datetime(
            year=2012,
            month=1,
            day=1,
            hour=12,
            minute=30,
            second=0)
        }
        mock_hub.publish.assert_called_once_with(key, bar)

        time.tick(timedelta(seconds=60))
        bars.on_tick(11)

        key = "{}:{}:{}:{}".format(
            COMPLETED_BAR,
            'exchange',
            'symbol',
            int(interval.total_seconds()))
        bar = {
        'open': 10,
        'high': 10,
        'low': 10,
        'close': 10,
        'start': datetime(
            year=2012,
            month=1,
            day=1,
            hour=12,
            minute=30,
            second=0)
        }

        key = "{}:{}:{}:{}".format(
            UPDATED_BAR,
            'exchange',
            'symbol',
            int(interval.total_seconds()))
        bar = {
            'open': 10,
            'high': 11,
            'low': 10,
            'close': 11,
            'start': datetime(
                year=2012,
                month=1,
                day=1,
                hour=12,
                minute=31,
                second=0)
        }
        mock_hub.publish.assert_any_call(key, bar)
        assert mock_hub.publish.call_count == 3


if __name__ == "__main__":
    unittest.main()
