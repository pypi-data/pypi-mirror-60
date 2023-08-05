# sufarray: implementation of suffix array

It uses prefix doubling for calculating the suffix array, which is O(n
log n) time.  When searching for all occurrences of a string, it takes
O(log n) time.  Further occurrences takes constant time.

At present the implementation is Python only.  This has the drawback
that the speed is not comparable with those of other languages.
