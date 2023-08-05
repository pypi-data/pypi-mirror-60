"""Sufarray: implementation of suffix array

While the performance is reasonable for smaller strings, it is quite
slow for long strings (e.g., of 100k in length).  Due to the
limitations of Python data structures, it is better to find C
implementations for such usages (not yet provided here).

"""

import array
import bisect
import enum
import functools
import itertools
import typing


# Prevent sort() from keeping all our suffixes to speed up the
# sorting, but that makes the module very memory hungry
@functools.total_ordering
class _SortKey:
    def __init__(self, text: str, pos: int) -> None:
        self.text = text
        self.pos = pos
    
    def __lt__(self, other: '_SortKey') -> bool:
        return self.text[self.pos:] < other.text[other.pos:]


class SufArrayBruteForce:
    """Represent a suffix array

    At present the implementation is not fast, but it will be
    optimized later.

    Args:
        text: The underlying text

    """
    def __init__(self, text: str) -> None:
        self._text = text
        self._array = self._compute_sufarray()

    def _compute_sufarray(self) -> typing.List[int]:
        def _key(pos: int) -> _SortKey:
            return _SortKey(self._text, pos)
        return sorted(range(len(self._text)), key=_key)

    def get_array(self) -> typing.List[int]:
        """Get the built suffix array

        If len(text) = n, then the returned array ret is a permutation
        of list(range(n)), where the suffix of text starting at
        position ret[i] is guaranteed to be less than that of ret[i+1]
        in lexicographic order, for all i from 0 to n-1.

        """
        return self._array

    def find_all(self, substr: str) -> typing.Iterable[int]:
        """Find the all occurrences of a string

        Args:
            substr: The string to search

        Returns:
            Generator of positions

        """
        left = self._bisect_left(substr)
        right = self._bisect_right(substr)
        while left < right:
            yield self._array[left]
            left += 1

    def _bisect_left(self, substr: str) -> int:
        # Return smallest i such that substr is smaller than or equal
        # to self._text[self._array[i] : self._array[i] +
        # len(substr)].  If there is no such i, return len(self._text)
        left = 0
        right = len(self._text)
        while left < right:
            mid = (left + right) // 2  # right will never be checked
            pos = self._array[mid]
            if substr <= self._text[pos : pos + len(substr)]:
                right = mid
            else:
                left = mid + 1
        return left

    def _bisect_right(self, substr: str) -> int:
        # Return largest i such that substr is larger than or equal to
        # self._text[self._array[i-1] : self._array[i-1] + len(substr)].
        # If there is no such i, return 0
        left = 0
        right = len(self._text)
        while left < right:
            mid = (left + right + 1) // 2  # left will never be checked
            pos = self._array[mid - 1]
            if substr >= self._text[pos : pos + len(substr)]:
                left = mid
            else:
                right = mid - 1
        return left


NameListType = typing.List[int]
PDDictType = typing.Dict[int, NameListType]
LcpLrType = typing.List[typing.Tuple[int, ...]]


class BisectState(enum.Enum):
    LEFT = 0
    RIGHT = 1
    START = 2


class SufArrayPD:
    """Represent a suffix array

    The suffix array is built using a simple prefix-doubling strategy.
    The time complexity upon construction of the object is O(n log n),
    and the time complexity for finding all substring is O(x + n log
    n), where x is the number of substring indices retrieved.

    Args:
        text: The underlying text

    """
    def __init__(self, text: str) -> None:
        self._text = text
        self._inv_sa = self._init_names()
        self._array = self._compute_sufarray()
        self._lcp = self._compute_lcp()
        self._lcp_lr = self._compute_lcp_lr()

    def _init_names(self) -> NameListType:  # Form order-preserving names
        if not self._text:
            return []
        return self._make_names(
            self._text,
            sorted(range(len(self._text)), key=lambda pos: self._text[pos]))

    def _compute_sufarray(self) -> typing.List[int]:
        cur_order = 0
        cur_len = 1
        while cur_len < len(self._text):
            names = self._prefix_double(cur_len)
            cur_order += 1
            cur_len *= 2
            if names == self._inv_sa:
                break
            self._inv_sa = names
        ret = [-1] * len(self._text)
        for pos, name in enumerate(self._inv_sa):
            ret[name] = pos
        return ret

    def _prefix_double(self, n_len: int) -> NameListType:
        names = self._inv_sa
        size = len(names)
        items = [names[pos] * (size + 1)
                 + (names[pos + n_len] if pos + n_len < size else -1)
                 for pos in range(size)]
        sorted_arr = sorted(list(range(size)), key=lambda pos: items[pos])
        return self._make_names(items, sorted_arr)

    @staticmethod
    def _make_names(items: typing.Union[str, typing.List[typing.Any]],
                    sorted_arr: NameListType) -> NameListType:
        ret = [-1] * len(items)
        name = -1
        last = None  # type: typing.Any
        for pos in range(0, len(items)):
            if items[sorted_arr[pos]] != last:  # Check for name update
                name = pos
                last = items[sorted_arr[pos]]
            ret[sorted_arr[pos]] = name
        return ret

    def _compute_lcp(self) -> typing.List[int]:
        size = len(self._text)
        cur_lcp = 0
        ret = [0] * (len(self._text) + 1)  # Add 1 for easy lcp_lr computation
        for suf_start in range(size):
            pos = self._inv_sa[suf_start]
            if pos == 0:
                cur_lcp = 0
                continue
            pred = self._array[pos - 1]
            while (suf_start + cur_lcp < size and
                   pred + cur_lcp < size and
                   self._text[suf_start + cur_lcp]
                   == self._text[pred + cur_lcp]):
                cur_lcp += 1
            ret[pos] = cur_lcp
            if cur_lcp:
                cur_lcp -= 1
        return ret

    def _compute_lcp_lr(self) -> LcpLrType:
        ret = [(0, 0)] * len(self._text)  # type: LcpLrType
        if self._text:
            self._update_lr(0, len(self._text), ret)
        return ret

    def _update_lr(self, left: int, right: int, lcp_lr: LcpLrType) -> int:
        # left and right are the same as the arguments during search.
        #
        # We update the mid entry of lcp_lr to a tuple (l, r), where l
        # = lcp(SA[left - 1], SA[mid]), and r = lcp(SA[mid],
        # SA[right]).  These allows mid to be checked during the
        # search without repeating to check already succeeding
        # characters.
        if right == left:  # Just propagate value out
            return self._lcp[left]
        if right == left + 1:  # mid == left
            lcp_lr[left] = (self._lcp[left], self._lcp[right])
            return min(lcp_lr[left])
        mid = (left + right) // 2
        lcp_l = self._update_lr(left, mid, lcp_lr)
        lcp_r = self._update_lr(mid + 1, right, lcp_lr)
        lcp_lr[mid] = (lcp_l, lcp_r)
        return min(lcp_l, lcp_r)

    def get_array(self) -> typing.List[int]:
        """Get the built suffix array

        If len(text) = n, then the returned array ret is a permutation
        of list(range(n)), where the suffix of text starting at
        position ret[i] is guaranteed to be less than that of ret[i+1]
        in lexicographic order, for all i from 0 to n-1.

        """
        return self._array

    def find_all(self, substr: str) -> typing.Iterable[int]:
        """Find the all occurrences of a string

        Args:
            substr: The string to search

        Returns:
            Generator of positions

        """
        pos, matched = self._bisect_left(substr)
        if matched:
            yield self._array[pos]
            for idx in range(pos + 1, len(self._array)):
                if self._lcp[idx] < len(substr):
                    break
                yield self._array[idx]

    def _bisect_left(self, substr: str) -> typing.Tuple[int, bool]:
        matched = 0
        state = BisectState.START
        left = 0
        right = len(self._text)
        while left < right:
            mid = (left + right) // 2  # left will never be checked
            pos = self._array[mid]
            done = False
            if state != BisectState.START:
                mid_lcp = self._lcp_lr[mid][
                    0 if state == BisectState.LEFT else 1]
                if mid_lcp < matched:  # original best still the best
                    if state == BisectState.LEFT:
                        right = mid
                    else:
                        left = mid + 1
                    done = True
                elif mid_lcp > matched:  # mid becomes the best
                    if state == BisectState.LEFT:
                        left = mid + 1
                    else:
                        right = mid
                    done = True
            if not done:  # First `matched` positions known to be matching
                cmp_res = 0
                for idx in range(matched, len(substr) + 1):
                    tpos = idx + pos
                    tord = -1 if tpos >= len(self._text) \
                           else ord(self._text[tpos])
                    sord = -1 if idx >= len(substr) else ord(substr[idx])
                    cmp_res = tord - sord
                    if cmp_res != 0:
                        break
                    if tord != -1:
                        matched += 1
                # cmp_res == cmp(text[pos:], substr[idx:])
                if cmp_res >= 0:
                    right = mid
                    state = BisectState.RIGHT
                else:
                    left = mid + 1
                    state = BisectState.LEFT
        return left, matched == len(substr)


SufArray = SufArrayPD
# SufArray = SufArrayBruteForce
