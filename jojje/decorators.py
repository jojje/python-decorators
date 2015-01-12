def equality(*atts, **kw):
    """
    Adds __eq__ and __hash__ functions to a class.
    
    Positional arguments:
    The names of the attributes to use for equality comparison and
    for calculating the object's hash code.
    
    Keyword argument:
    recompute -- Whether or not to recompute the hash code on each
                 call to the __hash__ function.
                 By default the hash code is computed only once,
                 the first time it is called. if passing this
                 parameter with a True value, the behavior is 
                 changed such that the hash value is recomputed each
                 time the hash function is called.
                 This is a boolean which defaults to False.
    
    The __eq__ function compares the named attributes (atts) of self 
    and the other object. As to the hash function, it computes
    the hash of self based on the XORed hashes of the values bound
    to the named attributes (atts) of the object.
    
    Example use:
    
      @equality('name','age')
      class Person:
          def __init__(self, name, age, mood):
              self.name = name
              self.age  = age
              self.mood = mood # some other att not used for eq checks
    
    Notes on optimization:
    The hash is optimized by calculating the hash value only once upon
    first call to the hash function, and then returning the same value 
    for subsequent calls. If attributes are changed while in a data 
    structure that relies on the hash, such as a dict, then the object 
    can only be found by using an object with the same named attributes 
    as was used when its counter part was initially stored in the data 
    structure.
    
    If the hash is to be recomputed each time the function is called,
    then care should be taken that the now mutable hash value doesn't
    change while the object is stored in structures that rely on the
    hash, else finding the object in those structures it will be
    difficult.
    
    The __eq__ method will always be computed for each call, and is
    unaffected by the optimize parameter. The implication of this is
    that if a hash collision happens in a data structure that replies
    on the hash code (e.g. dict), and if the hash is only computed once
    (default behavior), and  the attribute values used for the 
    comparison have changed, then that structure may be unable to find
    the object in the hash bucket it resides in.
    """
    
    if len(atts) == 0:
        raise ValueError("one or more attributes must be provided")
    
    recompute = kw['recompute'] if kw.has_key('recompute') else False
    
    def add_methods(cls):
                
        def eq(self,other):
            if not isinstance(other, self.__class__):
                return False
            for a in atts:
                if not getattr(self, a) == getattr(other, a):
                    return False
            return True
                            
        def compute_hash(self):
            ret = 0
            for a in atts:
                h = hash( repr( getattr(self, a) ) )
                ret ^= ret + h
            return ret

        def compute_hash_once(self):
            ret = compute_hash(self)
            setattr(self.__class__, '__hash__', lambda x: ret)
            return ret
        
        def pick_hash_func():
            return compute_hash if recompute else compute_hash_once
        
        setattr(cls, '__eq__', eq)
        setattr(cls, '__hash__', pick_hash_func())
        return cls
    
    return add_methods
    