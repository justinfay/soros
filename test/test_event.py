from unittest.mock import Mock

from soros.event import hub, subscribe


def test_subscribe():
    subscriber = Mock()
    hub.add_subscriber(subscriber, 'foo')
    hub.publish('foo', 1, 2, 3)
    subscriber.assert_called_once_with(1, 2, 3)
    hub.remove_subscriber(subscriber, 'foo')


def test_subscribe_decorator():
    subscriber = Mock()

    @subscribe('bar')
    def dummy(*args, **kwargs):
        subscriber(*args, **kwargs)

    hub.publish('bar', ['a', 'b', 'c'])
    subscriber.assert_called_once_with(['a', 'b', 'c'])
    hub.remove_subscriber(subscriber, 'bar')


def test_remove_subscriber():
    subscriber = Mock()
    hub.add_subscriber(subscriber, 'foo')
    hub.remove_subscriber(subscriber, 'foo')
    hub.publish('foo', 1, 2, 3)
    assert subscriber.call_count == 0


def test_two_subscribers():
    subscriber_1 = Mock()
    subscriber_2 = Mock()
    hub.add_subscriber(subscriber_1, 'foo')
    hub.add_subscriber(subscriber_2, 'foo')
    hub.publish('foo', 1, foo='bar')
    subscriber_1.assert_called_once_with(1, foo='bar')
    subscriber_2.assert_called_once_with(1, foo='bar')
    hub.remove_subscriber(subscriber_2, 'foo')
    hub.publish('foo', 'bar')
    assert subscriber_2.call_count == 1
    assert subscriber_1.call_count == 2
    hub.remove_subscriber(subscriber_1, 'foo')




