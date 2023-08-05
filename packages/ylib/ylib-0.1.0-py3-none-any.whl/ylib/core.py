#!/usr/bin/env python
# -*- coding: utf-8 -*-


def parse_triple_string(s: str, start_char: str = '|') -> str:
    r'''
    >>> parse_triple_string("|abc")
    'abc'
    >>> parse_triple_string("|abc\n    |bcd\n|cde\n")
    'abc\nbcd\ncde'
    >>> parse_triple_string("@abc\n    @bcd\n@cde\n", '@')
    'abc\nbcd\ncde'
    '''
    target_lines = s.split('\n')
    if target_lines[0] == '':
        target_lines = target_lines[1:]

    if target_lines[-1] == '':
        target_lines = target_lines[:-1]

    lines = []
    for line in target_lines:
        lines.append(line[line.index(start_char) + 1:])

    return '\n'.join(lines)


def include_poses(l, cond_f):
    """
    >>> list(include_poses(range(-1, 10), lambda x: x % 3 == 0))
    [1, 4, 7, 10]
    """
    for i, x in enumerate(l):
        if cond_f(x):
            yield i


def include_items(l, cond_f):
    """
    >>> list(include_items(range(-1, 10), lambda x: x % 3 == 0))
    [0, 3, 6, 9]
    """
    for x in l:
        if cond_f(x):
            yield x


def includes(l, cond_f):
    """
    >>> list(includes(range(-1, 10), lambda x: x % 3 == 0))
    [(1, 0), (4, 3), (7, 6), (10, 9)]
    """
    for i, x in enumerate(l):
        if cond_f(x):
            yield i, x
