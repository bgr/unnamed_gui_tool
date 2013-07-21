import collections


def duplicates(ls):
    """Returns list of elements that occur more than once in the given list."""
    return [el for el, n in collections.Counter(ls).items() if n > 1]


def with_rest(ls):
    """Generator - yields tuples (element, all_other_elements)"""
    for i, el in enumerate(ls):
        yield (el, ls[:i] + ls[i + 1:])


def with_succeeding(ls):
    """Generator - yields tuples (element, successor_elements)"""
    for i, el in enumerate(ls):
        yield (el, ls[i + 1:])


def with_preceding(ls):
    """Generator - yields tuples (element, predecessor_elements)"""
    for i, el in enumerate(ls):
        yield (el, ls[:i])


class _RecordMeta(type):

    def __new__(mcs, name, bases, dct):
        if len(bases) != 1 or (name != 'Record'
                               and not issubclass(bases[0], Record)):
            raise TypeError("Can only inherit from Record or its subclass")
        if dct.get('keys') is None:
            raise TypeError("Must specify mandatory 'keys' class variable")
        if not isinstance(dct['keys'], (tuple, list)):
            raise TypeError("Class variable 'keys' must be tuple or list")

        # prepend super's keys - subclass must have all keys its parent has:
        # collect keys starting from Record through its subclasses including
        # keys from class currently being built
        parent_keys = ([Par.keys for Par in reversed(bases[0].mro()[:-2])]
                       + [list(dct['keys'])])
        flat_keys = [k for pkeys in parent_keys for k in pkeys]

        # filter out duplicate keys, parents' keys are included
        # before any child's duplicate keys
        dct['keys'] = tuple(k for k, seen in with_preceding(flat_keys)
                            if k not in seen)

        return type.__new__(mcs, name, bases, dct)

    def __setattr__(cls, _, __):  # mainly to prevent modifying Class.keys
        raise TypeError("Nope")

#re.match("[_A-Za-z][_a-zA-Z0-9]*$",my_var)


class Record(tuple):
    __metaclass__ = _RecordMeta
    keys = ()

    def __new__(cls, *args, **keyvals):
        if len(args) + len(keyvals) != len(cls.keys):
            raise TypeError('{0} takes {1} items, got {2}'.format(
                cls.__name__, len(cls.keys), len(args) + len(keyvals)))

        # map positional args to as many keys as possible
        partial_keyvals = dict(zip(cls.keys, args))
        for key in partial_keyvals.keys():
            if key in keyvals:
                print keyvals
                raise TypeError("Argument '{0}' already specified "
                                "using positional arguments".format(key))

        for key in keyvals.keys():
            if key not in cls.keys:
                raise TypeError("Invalid keyword argument '{0}'".format(key))

        complete = dict(partial_keyvals.items() + keyvals.items())

        vals = tuple([complete[key] for key in cls.keys])  # order matters

        ret = super(Record, cls).__new__(cls, vals)
        return ret

    def __getattr__(self, key):
        return self[self.keys.index(key)]

    def __setattr__(self, _, __):
        raise TypeError('{0} is immutable'.format(self.__class__.__name__))

    def __setitem__(self, _, __):
        raise TypeError('{0} is immutable'.format(self.__class__.__name__))

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 ', '.join(['{0}={1}'.format(k, v) for k, v
                                            in zip(self.keys, self)]))
