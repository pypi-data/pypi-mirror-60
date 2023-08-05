#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Tuple, Union

TIME_TYPE = Union[int, float]


class TimeStruct:

    def __init__(self, tm_hour, tm_min, tm_sec):
        self.tm_hour, self.tm_min, self.tm_sec = self._regal(tm_hour, tm_min, tm_sec)

    @property
    def info(self):
        return (self.tm_hour, self.tm_min, self.tm_sec)

    @property
    def time_type(self) -> type:
        if any([type(self.info) == float]):
            return float
        else:
            return int

    def _regal(self, tm_hour: TIME_TYPE, tm_min: TIME_TYPE, tm_sec: TIME_TYPE)\
            -> Tuple[TIME_TYPE, TIME_TYPE, TIME_TYPE]:

        tm_type = _time_type(tm_hour, tm_min, tm_sec)
        sec = tm_type(tm_hour * 60 * 60 + tm_min * 60 + tm_sec)
        h = tm_type(sec // (60 * 60))
        m = tm_type(sec // 60) - h * 60
        s = tm_type(sec - m * 60 - h * 60 * 60)

        return h, m, s

    def __add__(self, other) -> TimeStruct:
        return TimeStruct(
            self.tm_hour + other.tm_hour, self.tm_min + other.tm_min, self.tm_sec + other.tm_sec)

    def __sub__(self, other) -> TimeStruct:
        return TimeStruct(
            self.tm_hour - other.tm_hour, self.tm_min - other.tm_min, self.tm_sec - other.tm_sec)

    def __mul__(self, c: TIME_TYPE) -> TimeStruct:
        return TimeStruct(c * self.tm_hour, c * self.tm_min, c * self.tm_sec)

    def __truediv__(self, c: TIME_TYPE) -> TimeStruct:
        c = float(c)
        return TimeStruct(self.tm_hour / c, self.tm_min / c, float(self.tm_sec) / c)

    def __int__(self) -> int:
        return int(self.tm_hour * 60 * 60 + self.tm_min * 60 + self.tm_sec)

    def __float__(self) -> float:
        return self.tm_hour * 60.0 * 60.0 + self.tm_min * 60.0 + self.tm_sec

    def __eq__(self, other) -> bool:
        return (
            self.tm_hour == other.tm_hour and self.tm_min == other.tm_min and
            self.tm_sec == other.tm_sec)

    def __str__(self) -> str:
        return f"TimeStruct<hour={self.tm_hour}, min={self.tm_min}, sec={self.tm_sec}>"


def _time_type(tm_hour: TIME_TYPE, tm_min: TIME_TYPE, tm_sec: TIME_TYPE):
    if any([type(t) is float for t in (tm_hour, tm_min, tm_sec)]):
        return float
    else:
        return int
