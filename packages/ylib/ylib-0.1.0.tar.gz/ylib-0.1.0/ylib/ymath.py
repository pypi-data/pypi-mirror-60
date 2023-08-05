#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import *  # noqa


def lcm(a: int, b: int) -> int:
    '''
    aとbの最小公倍数を計算する

    >>> lcm(1, 1)
    1
    >>> lcm(2, 3)
    6
    >>> lcm(6, 8)
    24
    >>> lcm(-6, 8)
    24
    >>> lcm(-6, -8)
    24
    >>> lcm(6, -8)
    24
    >>> lcm(0, 1)
    0
    >>> lcm(0, 0)
    0
    '''
    return 0 if a == 0 or b == 0 else abs(a * b) // gcd(a, b)  # noqa: F405


def is_prime(n: int) -> int:
    """
    nが素数か否かを判定する.
    nが1以下の場合は常にFalseを返す.

    >>> list(map(is_prime, range(-1, 5 + 1)))
    [False, False, False, True, True, False, True]
    """
    if n < 2:
        return False

    for i in range(2, n // 2 + 1):
        if n % i == 0:
            return False

    return True
