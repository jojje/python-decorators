# jojje.decorators

Collection of convenience decorators for Python.

The purpose is to eliminate tediousness and aspects prone to errors
during python development.  
The module will expand as I discover new patterns in Python that I want
to avoid repeating over and over and .. over.

At present it contains the following decorator.

## comparable

This is a class decorator with the purpose of simplifying the creation
of the `__lt__`, `__eq__` and `__hash__` methods. The motivation for
this is, aside from avoiding repetition in most every project, to ensure
consistency in establishing identity, equality and comparability for
objects.

If a class is to have a given set of member attributes used for
computing its unique identity, then the `eq` method would also be
assumed to evaluate those attributes, so there is generally a strong
coupling or at least correlation between the identity and equality
functions. There is also a correlation between an object's natural order
and how its identity is established, Since these three things generally
relate to some extent, it seems prudent to deal with them holistically,
as one unit or overall concern.

The use case prompting the decorator design and API is that I find
myself always wanting a class to compare some set of member attributes
whenever I see fit to bother with implementing custom identity and and
comparability. For most cases however the default Python implementation
suffices, where an object's identity is its unique location in memory.
Works great for dicts and sets in general. But.. when the need arises to
treat a (sub) set of an objects attributes as a kind of composite
identity key, there is a specific pattern I follow for implementing that
behavior, making sure also that equality comparison is aligned with the
properties used for the hash function, and this decorator is a
codification of that pattern, with natural ordering *provided for free*.

Example use:

```python 
@equality('attr_a', 'asc', 'attr_b', 'desc')
class C: 
    ...
```

where class is either a new or old style class and where `attr_a` and
`attr_b` are attributes that will be defined in the class before
comparison or hash (identity) checks are called.

The implemented `__lt__`  `__eq__` and `__hash__` functions each compare
and compute the specified attributes in turn, in the order listed in the
decorator's parameter list.

For more details, check out the extensive function documentation for
this decorator.
