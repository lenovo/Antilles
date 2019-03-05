# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import re


# Exception used for error reporting to the caller
class BadHostlist(Exception):
    pass


# Configuration to guard against ridiculously long expanded lists
MAX_SIZE = 100000
nsk_re = re.compile(r'([0-9]+)|([^0-9]+)')


def handle_int_nonint(int_nonint_tuple):
    if int_nonint_tuple[0]:
        return int(int_nonint_tuple[0])
    else:
        return int_nonint_tuple[1]


def numeric_sort_key(x):
    return [handle_int_nonint(i_ni) for i_ni in nsk_re.findall(x)]


def numerically_sorted(l):
    return sorted(l, key=numeric_sort_key)


def expand_part(s):
    # Base case: the empty part expand to the singleton list of ''
    if s == '':
        return ['']

    # Split into:
    # 1) prefix string (may be empty)
    # 2) rangelist in brackets (may be missing)
    # 3) the rest

    m = re.match(r'([^,\[]*)(\[[^\]]*\])?(.*)', s)
    (prefix, rangelist, rest) = m.group(1, 2, 3)

    # Expand the rest first (here is where we recurse!)
    rest_expanded = expand_part(rest)

    # Expand our own part
    if not rangelist:
        # If there is no rangelist, our own contribution is the prefix only
        us_expanded = [prefix]
    else:
        # Otherwise expand the rangelist (adding the prefix before)
        us_expanded = expand_rangelist(prefix, rangelist[1:-1])

    # Combine our list with the list from the expansion of the rest
    # (but guard against too large results first)
    if len(us_expanded) * len(rest_expanded) > MAX_SIZE:
        raise BadHostlist('results too large')

    return [us_part + rest_part
            for us_part in us_expanded
            for rest_part in rest_expanded]


def expand_rangelist(prefix, rangelist):
    # Split at commas and expand each range separately
    results = []
    for range_ in rangelist.split(','):
        results.extend(expand_range(prefix, range_))
    return results


def expand_range(prefix, range_):
    # Check for a single number first
    m = re.match(r'^[0-9]+$', range_)
    if m:
        return ['%s%s' % (prefix, range_)]

    # Otherwise split low-high
    m = re.match(r'^([0-9]+)-([0-9]+)$', range_)
    if not m:
        raise BadHostlist('bad range')

    s_low, s_high = m.group(1, 2)
    low = int(s_low)
    high = int(s_high)
    width = len(s_low)

    if high < low:
        raise BadHostlist('start > stop')
    elif high - low > MAX_SIZE:
        raise BadHostlist('range too large')

    results = []
    for i in xrange(low, high + 1):
        results.append('%s%0*d' % (prefix, width, i))
    return results


def remove_duplicates(l):
    seen = set()
    results = []
    for e in l:
        if e not in seen:
            results.append(e)
            seen.add(e)
    return results


def expand_hostlist(hostlist, allow_duplicates=False, sort=False):
    results = []
    bracket_level = 0
    part = ''

    for c in hostlist + ',':
        if c == ',' and bracket_level == 0:
            # Comma at top level, split!
            if part:
                results.extend(expand_part(part))
            part = ''
        else:
            part += c

        if c == '[':
            bracket_level += 1
        elif c == ']':
            bracket_level -= 1

        if bracket_level > 1:
            raise BadHostlist('nested brackets')
        elif bracket_level < 0:
            raise BadHostlist('unbalanced brackets')

    if bracket_level > 0:
        raise BadHostlist('unbalanced brackets')

    if not allow_duplicates:
        results = remove_duplicates(results)
    if sort:
        results = numerically_sorted(results)
    return results
