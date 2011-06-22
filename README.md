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
