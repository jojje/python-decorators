def comparable(*atts, **kwargs):
    """
    Adds __lt__, __eq__ and __hash__ functions to a class.

    Positional arguments:
      The arguments are pairs of strings with every odd element being
      the name of the attribute to be used by sorting and the even
      elements being the sorting order for the preceding attribute.

      Both attribute name and sorting order directives are strings.
      The attribute sorting order is one of 'asc' for ascending order
      and 'desc' for descending order.

      The attribute name may be substituted for a function which
      computes some arbitrary value instead of referring to an object's
      attribute. If a function is provided, it will be passed 'self' and
      is expected to return a value that can be compared to other
      objects of the same type.

      The rest of this documentation refers for simplicity only to
      attributes, but the reader should interpret such references to
      mean *either* an object's attribute, *or* the value computed by a
      provided function.

    Keyword argument:
    recompute -- Whether or not to recompute the hash code on each
                 call to the __hash__ function.
                 By default the hash code is computed only once,
                 the first time it is called. If passing this
                 parameter with a True value, the behavior is
                 changed such that the hash value is recomputed each
                 time the hash function is called.
                 This is a boolean which defaults to False.

    Description:
    The object's hash value is computed based on the values bound to the
    named attributes (atts) where the order of the listed attributes
    matter, in that different order of directives produce different hash
    codes.

    Equality is likewise based on checking the values of the listed
    attributes.

    Natural sort order is determined based on the order of the specified
    attribute names and whether the attribute should be evaluated
    (compared with another object) in ascending or descending order.
    If the first listed attribute holds the same value for both objects
    being compared, then a check of the next attribute in the atts list
    will be performed. Thus it continues until a difference is found or
    until all specified attributes have been tested, in which case the
    objects are determined to have an equal rank, and consequently the
    order between them is arbitrary (undefined).

    Example 1 -- named attributes:

      @comparable('name', 'asc', 'age', 'desc')
      class Person:
          def __init__(self, name, age, gender):
              self.name   = name
              self.age    = age
              self.gender = gender

      bobjr = Person('bob', 30, 'male')
      alice = Person('bob', 30, 'female')
      bobsr = Person('bob', 60, 'male')

      bobjr == alice           -> True
      bobsr < bobjr            -> True

      s = set((bobjr, alice))
      len(s)                   -> 1
      alice in s               -> True
      bobjr in s               -> True
      bobsr in s               -> False
      s.pop().gender           -> male

    This will provide natural ordering for Person based on a person's
    name in ascending order, followed by age in descending order. I.e.
    if two people have the same name, then age will be checked and if
    different will decide the raking of the two compared objects.

    Two Person objects with the same name and age will be considered to
    have the same identity (be identical) as both equality testing and
    hash code comparison will yield the same values for both objects.
    This holds true even if other attributes differ, such as one
    person's gender differing, since only the listed attributes are
    considered for the identity and equality checks.

    Example 2 -- use of partial identity function:

      @comparable('name', 'asc', lambda self: len(self.gender), 'desc')
      class Person:
          def __init__(self, name, age, gender):
              self.name   = name
              self.age    = age
              self.gender = gender

      bobjr = Person('bob', 30, 'male')
      alice = Person('bob', 30, 'female')
      bobsr = Person('bob', 60, 'male')

      bobjr != alice               -> True
      bobsr == bobjr               -> True

      s = set((bobjr, alice))
      len(s)                       -> 2
      alice in s                   -> True
      bobjr in s                   -> True
      bobsr in s                   -> True
      [ p.gender for p in \
        sorted([bobjr, alice]) ]   -> [female, male]

    In this slight variation of the first example, the secondary sorting
    directive is changed to a provided function that returns the length
    of a person's gender description. This means that if two people have
    the same name, what distinguishes them is the length of the person's
    gender description. Two people with the same name will have their
    comparative ranking determined by the gender description's length as
    well, so a person with a shorter gender description will be ranked
    higher than someone with a longer description.

    Note on optimization:
    The reason the recompute option exists is to provide the user
    control over which trade-off to make with regard to memory use
    versus successive lookup performance. By default an object's hash is
    looked up only once, and then cached on the attribute __hashcode__.
    Storing this integer value takes up a small amount of memory which
    may be a concern if the use case requires handling a large amount of
    objects.

    By instructing the decorator to recompute an object's hash code on
    each invocation thus saves a small bit of memory per object, but may
    incur a slight to significant processing overhead depending on how
    many attributes the composed hash key consists of (each specified
    attribute equals one hash calculation) and how many successive times
    an object is looked up.

    The default implementation adheres to the hashable requirement of
    Python, that "an object is hashable if it has a hash value which
    never changes during its lifetime", since the hash code is computed
    only once per object. If the hash code is recomputed, then care must
    be taken to  avoid changing any attributes which the hash code is
    based on while the object resides in a data structure that relies on
    object's hash code, such as a dict or set. Changing the dependent
    attributes while the object is in such data structures will make the
    data structure fail to locate the stored object.

    Note on side effects:
    Be aware that the decorator adds functions to the *actual class* it
    is attached to, that is it doesn't return a wrapper with the new
    functions. As such it is a method generator, not a delegate
    constructor as decorators typically are.
    """

    import inspect

    def pairs(atts):
        return list(zip( atts[0::2], atts[1::2] ))

    # Speeds up lookup by pre-determining the right mechanism to resolve
    # the attribute value, so we can avoid doing conditional branching
    # in tight loops (optimization)
    def append_attr_getters(atts):
        def isfunc(att):
            return hasattr(att,'__call__')
        def pick_getter(att):
            return (lambda obj, att: att(obj)) if isfunc(att) else getattr
        return [( att, order, pick_getter(att) ) for (att,order) in pairs(atts)]

    def validate():

        if len(atts) == 0:
            raise ValueError("attribute(s) for sorting must be provided")

        if inspect.isclass(atts[0]):
            raise ValueError("must be provided attribute and order aguments")


        if not len(atts) % 2 == 0:
            raise ValueError("must have an even number of attribute and "+ \
                             "sorting order arguments")

        for a, v in pairs(atts):
            if not v in ('asc', 'desc'):
                raise ValueError("invalid sorting order for attribute {}: {}" \
                                .format(a,v))

    validate()

    recompute  = kwargs['recompute'] if ('recompute') in kwargs else False
    att_list   = append_attr_getters(atts)

    def add_methods(cls):

        def lt(self, other):
            if not isinstance(other, self.__class__):
                raise ValueError("compared objects not of the same type")

            ret = None
            for att, order, geta in att_list:
                a, b = geta(self, att), geta(other, att)

                if order == 'desc':
                    b, a = a, b

                if a < b:
                    return True

            return False

        def eq(self,other):
            if not isinstance(other, self.__class__):
                return False
            for att, order, geta in att_list:
                if not geta(self, att) == geta(other, att):
                    return False
            return True

        def compute_hash(self):
            ret = 0
            for att, order, geta in att_list:
                h = hash( repr( geta(self, att) ) )
                ret ^= ret + h
            return ret

        def compute_hash_once(self):
            if '__hashcode__' not in self.__dict__:
                self.__hashcode__ = compute_hash(self)
            return self.__hashcode__

        def pick_hash_func():
            return compute_hash if recompute else compute_hash_once

        setattr(cls, '__lt__', lt)
        setattr(cls, '__eq__', eq)
        setattr(cls, '__hash__', pick_hash_func())
        return cls

    return add_methods
