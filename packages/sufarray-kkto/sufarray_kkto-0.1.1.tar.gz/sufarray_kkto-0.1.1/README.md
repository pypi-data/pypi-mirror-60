# sufarray: implementation of suffix array

It uses prefix doubling for calculating the suffix array, which is O(n
log n) time.  When searching for all occurrences of a string, it takes
O(log n) time.  Further occurrences takes constant time.

At present the implementation is Python only.  This has the drawback
that the speed is not comparable with those of other languages.

## Usage

To construct a suffix array of string `s`:

    import sufarray
    sarray = sufarray.SufArray(s)

After that, you can get the actual array with:

    sarray.get_array()
    
This produces a permutation `a` of `range(len(s))`, where the values
`a[0]`, `a[1]`, etc. are such that the suffixes `s[a[i]:]` is sorted.

Other than that, you can find the positions where a string `n` appears
within `s` using:

    sarray.find_all(n)

This is a generator function, yielding all the possible positions.

## Implementations

Two implementations are provided.  The simple version is called
`SufArrayBruteForce`, and a version `SufArrayPD` is provided which
calculates the suffix array using prefix doubling, and augment the
result with a LCP (Longest common prefix) array for use with
searching.  The latter has better bounded performance guarantees, but
with arrays of small text it is slower.  The default is `SufArrayPD`.
You can use the brute force version using
`sufarray.SufArrayBruteForce`.
