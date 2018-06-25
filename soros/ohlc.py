"""
Bar generation from tick data.
"""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import math

from .constants import *
from .event import hub


class OHLC:
    """
    A bar (OHLC) creator and provider.
    """

    def __init__(
            self,
            exchange,
            symbol,
            interval=timedelta(minutes=1),
            bars=None,
            max_bars=60*60*24*7):
        self.exchange = exchange
        self.symbol = symbol
        self.interval = interval
        self._bars = bars if bars is not None else []
        self.max_bars = max_bars
        self.current_bar = None

        # Set this as a listener for ticks.
        key = "{}:{}:{}".format(TICK, self.exchange, self.symbol)
        hub.add_subscriber(self.on_tick, key)

    def on_tick(self, price):
        """
        Feed a new price tick into the Bar compiler.
        """
        if self.current_bar is None:
            self._first_bar(price)
        elif datetime.utcnow() >= self.interval + self.current_bar['start']:
            # Publish the complete bar.
            key = "{}:{}:{}:{}".format(
                COMPLETED_BAR,
                self.exchange,
                self.symbol,
                int(self.interval.total_seconds()))
            hub.publish(key, self.current_bar)
            self._new_bar(price)
        else:
            self._update_bar(price)
        # Publish the current bar.
        key = "{}:{}:{}:{}".format(
            UPDATED_BAR,
            self.exchange,
            self.symbol,
            int(self.interval.total_seconds()))
        hub.publish(key, self.current_bar)

    def _first_bar(self, price):
        """
        Create the first bar.
        """
        bar = {}
        bar['open'] = price
        bar['high'] = price
        bar['low'] = price
        bar['close'] = price
        # We want to always have a bar start at midnight,
        # But we fast forward to the closest segment.
        start_datetime = datetime.combine(date.today(), time())
        now = datetime.utcnow()
        while now > start_datetime + self.interval:
            start_datetime += self.interval
        bar['start'] = start_datetime

        self.current_bar = bar

    def _new_bar(self, price):
        """
        Add a new bar.
        """
        # Handle case where we missed a tick for a complete interval.
        count_bars_since_current = math.floor(
            (datetime.utcnow() - self.current_bar['start'])
            / self.interval)
        for _ in range(count_bars_since_current - 1):
            bar = self.current_bar.copy()
            bar['start'] = self.current_bar['start'] + self.interval
            self._bars.append(self.current_bar)
            self.current_bar = bar
        bar = {}
        bar['open'] = self.current_bar['close']
        if price > self.current_bar['high']:
            bar['high'] = price
        else:
            bar['high'] = self.current_bar['high']
        if price < self.current_bar['low']:
            bar['low'] = price
        else:
            bar['low'] = self.current_bar['low']
        bar['close'] = price
        bar['start'] = self.current_bar['start'] + self.interval
        self._bars.append(self.current_bar)
        if len(self._bars) == self.max_bars:
            self._bars.pop(0)
        self.current_bar = bar

    def _update_bar(self, price):
        """
        Update the current bar.
        """
        if price > self.current_bar['high']:
            self.current_bar['high'] = price
        if price < self.current_bar['low']:
            self.current_bar['low'] = price
        self.current_bar['close'] = price

    def bars(self, n=60):
        """
        Return the last `n` bars.
        """
        # TODO: Call load bar if needed.
        if self.current_bar is None:
            return []
        return [*self._bars[-(n-1):], self.current_bar]
