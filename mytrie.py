"""
`mytrie.py` -- Generic tries for Python
=====================================

Copyright 2011 by Max Bane.  
Distributed subject to the Creative Commons Attribution 3.0 Unported license (CC
BY 3.0): http://creativecommons.org/licenses/by/3.0/

A library of generic Trie data structures
-----------------------------------------

A _trie_ (rhymes with "sky") is a [tree-based data
structure](http://en.wikipedia.org/wiki/Trie) that is useful for space-efficient
storage or mapping of strings and string-like sequences, and for quickly finding
string prefixes, suffixes, extensions, and so on.

`TODO`

String-like types
-----------------

The trie classes provided by this module are fully generic, in that they work
with any user-defined key type that is "string-like" in the following sense.

A type `t` is a set of python objects. The members of `t` are called instances
of `t`.  An object is string-like if it is an instance of a string-like type. A
type `t` is string-like iff:

  - 1. for all instances `o` of type `t`:
      - 1a. `o` is iterable
      - 1b. `o` is hashable
      - 1c. `(o in o) is True`
  - 2. there exists some null instance e of type t such that for all
    instances o of type t:
      - 2a. `(e in o) is True`
      - 2b. `(e + o == o + e == o) is True`
      - 2c. `(reduce(operator.add, o, e) == o) is True`

Note that python `str` instances have all of these properties and more (e.g.,
`o[:] == o`), but that the properties enumerated above are all that must be
statisfied for a type to be considered "string-like" in this module.

Note also that, by this definition, tuples are NOT string-like, as they fail
condition 2c. In fact, the python `str` type is the only built-in type that is
string-like. 

(Exercise: prove that any string-like object is itself a *sequence* of
string-like objects.)

It is expected that string-like types to be used with this module (other than
`str`) will be implemented through user-defined classes; the above definition
gives exactly the conditions that must be met by the interface of any such class
to function properly with this module.  

The module-level function `isStringLike` is provided to assist you in
determining whether your custom types are string-like.

Furthermore, a fully general `StringLike` class is provided, which is capable of
representing sequences of of objects of any (possibly heterogeneous) types, and
satisfying the conditions of string-likeness for use with the generic trie
classes. 

You should thus be able to use this module to construct tries of any sequential
data structure for which the concept makes sense: tries of character strings,
tries of word tokens, tries of paths in an arbitrary graph, and so on.

Examples
--------

See the method docstrings below for more examples.

`TODO`

END MODULE DOC
"""

__version__ = "0.1.0"

import operator

def isStringLike(obj, nullObj):
    """
    Return True iff obj *could* be an instance of a string-like type, as
    defined in the module docstring, with the given null instance. A type is
    string-like iff this function returns True on *every* possible instance of
    it (of course most types have an infinitude of possible instances).

    >>> isStringLike('', '')
    True

    >>> isStringLike('hello world', '')
    True

    >>> isStringLike('hello world', 'a')
    False

    >>> isStringLike((1,2), ())
    False

    """
    try:
        hash(obj)
        return  ((nullObj in obj) is True) and \
                ((nullObj + obj == obj + nullObj == obj) is True) and \
                ((obj in obj) is True) and \
                ((reduce(operator.add, obj, nullObj) == obj) is True)
    except:
        return False

#===============================================================================

class TrieBase(object):
    def __init__(self, null_element):
        self._null_element = null_element

        if not isStringlike(null_element, null_element):
            raise TypeError('null_element %r is not itself string-like!' %\
                    (null_element,))

        # subclasses should create a root node. nodes are lists of length >= 2,
        # whose first element is a dictionary from elements to associated
        # subnodes, second element is bool indicating whether a key terminates
        # at the node.

    def __contains__(self, key):
        cur_node = self._root
        for el in key:
            try:
                cur_node = cur_node[0][el]
            except KeyError:
                return False
        return cur_node[1]

    def __nodeOf(self, key):
        cur_node = self._root
        for el in key:
            try:
                cur_node = cur_node[0][el]
            except KeyError:
                return None
        return cur_node

    def has_prefix(self, prefix):
        """
        Return True if the given string-like is a prefix of any contained element.

        """
        return self.__nodeOf(prefix) is not None

    def __pathTo(self, key):
        cur_node = self._root
        for el in key:
            yield cur_node
            # let KeyError propagate
            cur_node = cur_node[0][el]
        yield cur_node

    def __generateKeys(self, cur_node=None, prefix=None):
        cur_node = cur_node or self._root
        prefix = prefix or self._null_element
        if cur_node[1]:
            yield prefix
        for el, el_node in cur_node[0].iteritems():
            for member in self.__generateKeys(el_node, prefix+el):
                yield member

    __iter__ = __generateKeys

    # Slower -- using an explicit stack
    #def __iter__(self):
    #    # special case for null element
    #    if self._root[1]:
    #        yield self._null_element

    #    # depth-first enumeration
    #    stack = [(self._null_element+el, el_node) for \
    #            el, el_node in self._root[0].iteritems()]
    #    
    #    while stack:
    #        prefix, cur_node = stack.pop()
    #        if cur_node[1]:
    #            yield prefix
    #        for el, el_node in cur_node[0].iteritems():
    #            stack.append((prefix+el, el_node))

    def __len__(self):
        # should be equivalent to len(list(self)), but faster
        stack = [el_node for el_node in self._root[0].itervalues()]
        n = 0
        
        while stack:
            cur_node = stack.pop()
            if cur_node[1]:
                n += 1
            for el_node in cur_node[0].itervalues():
                stack.append(el_node)

        return n

    def update(self, *args):
        raise NotImplementedError
            
    def successors(self, prefix):
        """
        Generate (in arbitrary order) those prefixes of contained keys that
        are "successors" of the given prefix, i.e., that are 1-symbol extensions
        thereof.

        Raise a KeyError if the given prefix is not a prefix of any contained
        element.

        """

        # find the node where the given prefix ends, if any
        node = self.__nodeOf(prefix)
        if node is None:
            raise KeyError('%r is not a prefix of any contained element.' %\
                    prefix)
        for el in node[0].iterkeys():
            yield prefix + el

    def __generateSubNodes(self, start_node, prefix):
        yield start_node, prefix
        for el, el_node in start_node[0].iteritems():
            for node, subel in self.__generateSubNodes(el_node, prefix+el):
                yield node, subel

    def extensions(self, prefix, members_only=True):
        """
        Generate, in arbitrary order, those strings which are extensions of the
        given prefix, and either:
            - contained keys themselves if members_only is True (the
              default), or
            - prefixes of contained keys if members_only is False.

        If the given prefix is not a prefix of any contained element, raise a
        KeyError.

        """
        
        # find the node where the given prefix ends, if any
        node = self.__nodeOf(prefix)
        if node is None:
            raise KeyError('%r is not a prefix of any contained element.' %\
                    prefix)

        for node, suff in self.__generateSubNodes(node, prefix):
            if (not members_only) or node[1]:
                yield suff


#===============================================================================

class TrieSet(TrieBase):
    r"""
    Space-efficient storage of unique strings, with fast enumeration of string
    extensions, successors, prefix testing, and prefix matching. Generally
    emulates the interface of the built-in set type.

    Elements must be string-like, and once added to the TrieSet, cannot be
    removed (unlike a built-in set).

    If given, contents should be a sequence of string-like objects with which to
    initially populate the TrieSet. 

    null_element, if given, should be the null object for whatever string-like
    type will be added to the TrieSet (see module documentation for definitions).
    If not given, it defaults to '', the null element for type str.

    >>> t = TrieSet(['abc', 'aac', 'adc', 'adce'])
    >>> 'abc' in t
    True

    >>> '' in t
    False

    >>> 'xxx' in t
    False

    >>> t.add('xxx')
    >>> 'xxx' in t
    True

    >>> len(t)
    5

    >>> sorted(list(t))
    ['aac', 'abc', 'adc', 'adce', 'xxx']

    >>> t.has_prefix('a')
    True

    >>> t.has_prefix('ad')
    True

    >>> t.has_prefix('abc')
    True

    >>> t.has_prefix('b')
    False

    >>> t.has_prefix('')
    True

    >>> set(t.successors('a')) == set(['ab', 'aa', 'ad'])
    True

    >>> set(t.successors('ad')) == set(['adc'])
    True

    >>> set(t.successors('abc')) == set()
    True

    >>> set(t.successors('b'))
    Traceback (most recent call last):
        ...
    KeyError: "'b' is not a prefix of any contained element."

    >>> set(t.extensions('ad')) == set(['adc', 'adce'])
    True

    >>> set(t.extensions('adc')) == set(['adc', 'adce'])
    True

    >>> set(t.extensions('a')) == set(['abc', 'aac', 'adc', 'adce'])
    True

    >>> set(t.extensions('a', members_only=False)) == \
    ...     set(['a', 'ab', 'aa', 'ad', 'abc', 'aac', 'adc', 'adce'])
    True

    >>> set(t.extensions('abc')) == set(['abc'])
    True

    >>> set(t.extensions('')) == set(t)
    True

    >>> set(t.extensions('', members_only=True)).issuperset(set(t))
    True

    >>> set(t.extensions('b'))
    Traceback (most recent call last):
        ...
    KeyError: "'b' is not a prefix of any contained element."

    """

    def __init__(self, contents=None, null_element=''):
        super(TrieSet, self).__init__(null_element)

        # [suffixes, is_member]
        self._root = [{}, False]

        if contents is not None:
            self.update(contents)

    def __repr__(self):
        """
        >>> t = TrieSet(map(str, xrange(1000)))
        >>> t == eval(repr(t))
        True

        """
        return 'TrieSet(%r, null_element=%r)' % (list(self),
                self._null_element)

    def __eq__(self, trieSet):
        """
        >>> t = TrieSet()
        >>> t == t
        True

        >>> TrieSet() == TrieSet()
        True

        >>> TrieSet(['a', 'b']) == TrieSet(['a', 'b', 'a'])
        True

        >>> TrieSet(['a', 'b']) == TrieSet(['a'])
        False

        """
        return self.issubset(trieSet) and trieSet.issubset(self)

    def add(self, key):
        """
        Add an element, which must be string-like.

        >>> t = TrieSet()
        >>> '' in t
        False

        >>> t.add('')
        >>> t.add('a')
        >>> '' in t
        True

        >>> 'a' in t
        True

        >>> 'b' in t
        False
        """

        if not isStringlike(key, self._null_element):
            raise TypeError('Key must be string-like with null element %r! '\
                    '(got %r)' % (self._null_element, key))

        cur_node = self._root
        for el in key:
            try:
                cur_node = cur_node[0][el]
            except KeyError:
                new_node = [{}, False]
                cur_node[0][el] = new_node
                cur_node = new_node

        cur_node[1] = True # is_member

    def update(self, keys):
        """
        Add elements to a TrieSet. Raise a TypeError if the given object is not
        a sequence of string-like objects.

        >>> t = TrieSet(['abc'])
        >>> t.update(['hello', 'world'])
        >>> 'abc' in t and 'hello' in t and 'world' in t
        True
        """
        for key in keys:
            self.add(key)


    def union(self, trieset):
        """
        Return a new TrieSet whose contents are the union of two TrieSets. Raise
        a ValueError if the two TrieSets have different null_elements.

        >>> t1 = TrieSet(['abc', 'aac', 'adc', 'adce'])
        >>> t2 = TrieSet(['dfe', 'def', 'dd', 'x'])
        >>> t1.union(t2) == TrieSet(['aac', 'abc', 'adc', 'adce', 'x', 'def', 'dd', 'dfe'])
        True

        >>> t1.union(t2) == t2.union(t1)
        True

        >>> t1 | t2 == t1.union(t2)
        True
        """

        if self._null_element != trieset._null_element:
            raise ValueError

        return TrieSet(set(self)|set(trieset), null_element=self._null_element)

    __or__ = union

    def intersection(self, trieset):
        """
        Return a new TrieSet whose contents are the intersection of two TrieSets. Raise
        a ValueError if the two TrieSets have different null_elements.

        >>> t1 = TrieSet(['abc', 'aac', 'adc', 'adce'])
        >>> t2 = TrieSet(['dfe', 'adc', 'dd', 'abc'])
        >>> t1.intersection(t2) == TrieSet(['abc', 'adc'])
        True

        >>> t1.intersection(t2) == t2.intersection(t1)
        True

        >>> t1 & t2 == t1.intersection(t2)
        True
        """

        if self._null_element != trieset._null_element:
            raise ValueError

        return TrieSet(set(self)&set(trieset), null_element=self._null_element)

    __and__ = intersection

    def issubset(self, trieset):
        """
        Return True iff this TrieSet contains a subset of the elements of the
        given TrieSet.

        >>> TrieSet().issubset(TrieSet())
        True

        >>> TrieSet().issubset(TrieSet(['']))
        True

        >>> TrieSet(['a']).issubset(TrieSet(['', 'a']))
        True

        >>> TrieSet(['a']).issubset(TrieSet())
        False
        """
        for element in self:
            if element not in trieset:
                return False
        return True

    def issuperset(self, trieset):
        """
        Return True iff this TrieSet contains a subset of the elements of the
        given TrieSet.

        >>> TrieSet().issuperset(TrieSet())
        True

        >>> TrieSet().issuperset(TrieSet(['']))
        False

        >>> TrieSet(['a']).issuperset(TrieSet(['', 'a']))
        False

        >>> TrieSet(['a']).issuperset(TrieSet())
        True
        """
        return trieset.issubset(self)

#===============================================================================

class TrieDict(object):
    """
    An associative trie for space-efficiently mapping string-like keys to
    arbitrary values, with fast enumeration of key extensions, successors,
    prefix testing, and prefix matching. Generally emulates the interface of the
    built-in dict type.

    Keys must be string-like, and once added to the TrieDict, cannot be removed
    (unlike a built-in dict).

    If given, items should be one of the following:
        - a sequence of (key, value) tuples with which to initially populate the
          TrieDict;
        - an object with keys() and __getitem__() methods (such as a built-in
          dict or another TrieDict) from which to initially populate the
          TrieDict.

    null_element, if given, should be the null object for whatever string-like
    type will be added to the TrieSet (see module documentation for definitions).
    If not given, it defaults to '', the null element for type str.
    """

    def __init__(self, items=None, null_element=''):
        super(TrieSet, self).__init__(null_element)

        # [suffixes, is_member, value]
        self._root = [{}, False, None]

        if items is not None:
            self.update(items)

    def __repr__(self):
        return 'TrieDict(%r, null_element=%r)' % (self.items(),
                self._null_element)

    def __setitem__(self, key, value):
        pass

    def __getitem__(self, key, value):
        pass

    def iteritems(self):
        pass

    def items(self):
        pass

    def keys(self):
        pass

    def iterkeys(self):
        pass

    def values(self):
        pass

    def itervalues(self):
        pass

#===============================================================================

class StringLike(object):
    """
    Provides a string-like type for representing immutable sequences of tokens,
    where a token is an arbitrary object. Essentially a thin wrapper around the
    tuple type, with the key differences for string-likeness being the
    implementations of __iter__, __getitem__, and __contains__.
    """

    Empty = None # reassigned below

    def __init__(self, tokens=None):
        self.tokens = tuple(tokens) if tokens else ()

    def __bool__(self):
        return bool(self.tokens)

    def __repr__(self):
        if self:
            return 'StringLike(%r)' % (self.tokens,)
        return 'StringLike.Empty'

    def __hash__(self):
        return hash(self.tokens)

    def __getitem__(self, i):
        return StringLike((self.tokens[i],))

    def __cmp__(self, other):
        return cmp(self.tokens, other.tokens)

    def __iter__(self):
        for tok in self.tokens:
            yield StringLike((tok,))

    def __len__(self):
        return len(self.tokens)

    def __add__(self, other):
        return StringLike(self.tokens + other.tokens)

    def __contains__(self, other):
        if other == StringLike.Empty:
            return True
        for match in KnuthMorrisPratt(self, other):
            return True
        return False

StringLike.Empty = StringLike()

#===============================================================================

# Modified slightly for efficiency by Max Bane, 2011 -- python implementation of
# the Knuth-Morris-Pratt substring search algorithm for generic iterables.
## {{{ http://code.activestate.com/recipes/117214/ (r1)
# Knuth-Morris-Pratt string matching
# David Eppstein, UC Irvine, 1 Mar 2002

def KnuthMorrisPratt(text, pattern):
    '''
    Yields all starting positions of copies of the pattern in the text.
    Calling conventions are similar to string.find, but its arguments can be
    lists or iterators, not just strings, it returns all matches, not just the
    first one, and it does not need the whole text in memory at once.  Whenever
    it yields, it will have read the text exactly up to and including the match
    that caused the yield.
    '''

    # allow indexing into pattern and protect against change during yield
    #pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in xrange(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            yield startPos
## end of http://code.activestate.com/recipes/117214/ }}}

#===============================================================================


if __name__ == "__main__":
    import doctest
    doctest.testmod()
