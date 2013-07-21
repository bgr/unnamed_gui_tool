import collections


def duplicates(ls):
    """Returns list of elements that occur more than once in the given list."""
    return [el for el, n in collections.Counter(ls).items() if n > 1]


class _RecordMeta(type):
    def __setattr__(self, _, __):
        raise TypeError("Nope")


class Record(tuple):
    __metaclass__ = _RecordMeta
    keys = ()

    def __new__(cls, *args, **keyvals):
        if len(args) + len(keyvals) != len(cls.keys):
            raise TypeError('{0} takes {1} items, got {2}'.format(
                cls.__name__, len(cls.keys), len(args) + len(keyvals)))

        partial_keyvals = dict(zip(cls.keys, args))
        for key in partial_keyvals.keys():
            if key in keyvals:
                raise TypeError("Argument '{0}' already specified "
                                "using positional arguments".format(key))

        for key in keyvals.keys():
            if key not in cls.keys:
                raise TypeError("Invalid keyword argument '{0}'".format(key))

        complete_keyvals = dict(partial_keyvals.items() + keyvals.items())

        # order of values matters
        vals = tuple([complete_keyvals[key] for key in cls.keys])

        ret = tuple.__new__(cls, vals)
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
