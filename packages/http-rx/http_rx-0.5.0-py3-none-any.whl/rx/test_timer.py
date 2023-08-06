import pytest
import sys, time

from .timer import PerpetualTimer


def test_timer():
    def timer_func(results):
        results.append(0)

    nums = []
    t = PerpetualTimer(0.01, timer_func, args=(nums,))
    assert not t._should_continue
    assert t.thread is None
    t.cancel()
    assert not t._should_continue
    assert t.thread is None
    t._start_timer()
    assert not t._should_continue
    assert t.thread is None

    t.start()
    assert t._should_continue
    t.start()
    assert t._should_continue
    assert t._should_continue
    time.sleep(0.05)
    t.cancel()
    nums_len = len(nums)
    assert 4 <= len(nums) <= 6
    time.sleep(0.02)
    assert len(nums) == nums_len
