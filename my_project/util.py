import re
import collections
#from inspect import getargspec as _getargspec
from keyword import iskeyword as _iskeyword


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



def is_valid_identifier(str_val):
    return (not _iskeyword(str_val) and
            re.match("[_A-Za-z][_a-zA-Z0-9]*$", str_val) is not None)


class _RecordMeta(type):

    def __new__(mcs, name, bases, dct):
        # don't allow inheriting from multiple bases as a precaution
        if len(bases) != 1:
            raise TypeError("Inheriting from multiple bases is not supported")
        # allow to leave 'keys' unspecified to just inherit parents' keys
        if dct.get('keys') is None:
            dct['keys'] = ()
        elif not isinstance(dct['keys'], (tuple, list)):
            raise TypeError("Class variable 'keys' must be tuple or list")

        # build complete keys tuple by prepending keys of superclasses since
        # subclass must have all keys its bases have. collect keys starting
        # from Record through the subclasses and finally keys from class
        # currently being built
        parent_keys = ([Par.keys for Par in reversed(bases[0].mro()[:-2])]
                       + [list(dct['keys'])])
        flat_keys = [k for pkeys in parent_keys for k in pkeys]

        # keys must also be valid identifiers
        invalid = [k for k in flat_keys if not is_valid_identifier(k)]
        if invalid:
            raise TypeError("Invalid keys: {0}".format(', '.join(invalid)))

        # filter out duplicate keys, parents' keys have precedence and come
        # before any child's duplicate keys
        complete_keys = tuple(k for k, seen in with_preceding(flat_keys)
                              if k not in seen)
        dct['keys'] = complete_keys

        # now that we have complete keys, check if 'prepare' method
        # is valid - all parameter names must be valid key names
        # we cannot check that it will return valid dict though
        # DISABLED since jython's classmethod object doesn't have __func__
        #prep = dct.get('prepare')
        #if prep and not all(arg in complete_keys
        #                    for arg in _getargspec(prep.__func__).args):
        #    raise TypeError("Parameter names of 'prepare' must match 'keys'")

        return type.__new__(mcs, name, bases, dct)

    def __setattr__(cls, _, __):  # mainly to prevent modifying Class.keys
        raise TypeError("Nope")


# TODO: recordInstance.make(newparams)

class Record(tuple):
    __metaclass__ = _RecordMeta
    keys = ()

    def __new__(cls, *args, **kwargs):
        n_args = len(args) + len(kwargs)
        n_keys = len(cls.keys)
        has_prepare = hasattr(cls, 'prepare')
        # accept less arguments if there is prepare function which might
        # take care of default values
        if n_args > n_keys and has_prepare:
            raise TypeError("Too many arguments, {0} takes at most {1} items, "
                            "got {2}".format(cls.__name__, n_keys, n_args))
        elif n_args != n_keys and not has_prepare:
            raise TypeError("{0} takes exactly {1} items, got {2} (you can "
                            "add 'prepare' function to implement default "
                            "values)".format(cls.__name__, n_keys, n_args))

        # map positional args to as many keys as possible
        positional = dict(zip(cls.keys, args))
        for key in positional.keys():
            if key in kwargs:
                raise TypeError("Argument '{0}' already specified "
                                "using positional arguments".format(key))
        for key in kwargs.keys():
            if key not in cls.keys:
                raise TypeError("Invalid keyword argument '{0}'".format(key))

        # all key-value pairs that were passed when instantiating
        gathered = dict(positional.items() + kwargs.items())
        # pass them to 'prepare' function if there is one
        if has_prepare:
            prepared = cls.prepare(**gathered)
            # prepare might return new keys, check if they're valid
            if any(k not in cls.keys for k in prepared.keys()):
                raise TypeError("'prepare' must return dict with keys that "
                                "match {0}.keys".format(cls.__name__))
            # overwrite values in gathered with prepared
            gathered.update(prepared)

        missing = [k for k in cls.keys if k not in gathered.keys()]
        if missing:
            raise TypeError("Missing values for: {0}".format(
                            ', '.join(missing)))

        vals = tuple([gathered[key] for key in cls.keys])  # order matters

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
