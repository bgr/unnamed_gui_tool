import collections
import inspect
from copy import copy


def duplicates(ls):
    """Returns list of elements that occur more than once in the given list."""
    return [el for el, n in collections.Counter(ls).items() if n > 1]


def remove_duplicates(ls, key=lambda el: el):
    """Returns new list with removed redundant elements, keeps order."""
    seen = set()
    add_to_seen = lambda elem: not seen.add(elem)  # always returns True
    return [elem for elem in ls
            if key(elem) not in seen and add_to_seen(key(elem))]


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


def join_dicts(*dicts):
    """Joins two dictionaries (dumb, will discard some value if same keys)."""
    return dict(reduce(list.__add__, [d.items() for d in dicts]))


def fseq(*functions):
    """ Wraps given functions into single function that will, when called, call
        all functions in given sequence in the order they were given, passing
        the arguments to every function. Return value of the wrapper function
        is list of return values of each function.
    """
    return lambda *args, **kwargs: [f(*args, **kwargs) for f in functions]


def bounding_box_around_points(point_list):
    def expand_box(current_box, new_point):
        min_x, min_y, max_x, max_y = current_box
        x, y = new_point
        return (min(min_x, x), min(min_y, y), max(max_x, x), max(max_y, y))
    neg_inf = float("-inf")
    pos_inf = float("inf")
    return reduce(expand_box, point_list, (pos_inf, pos_inf, neg_inf, neg_inf))


def partition(ls, pred=lambda el: el):
    """ Partitions list (or other iterable) into two lists and returns tuple
        (matched_elems_list, unmatched_elems_list).
    """
    matched, unmatched = [], []
    for el in ls:
        if pred(el):
            matched.append(el)
        else:
            unmatched.append(el)
    return (matched, unmatched)


#def is_valid_identifier(str_val):
#    return (not keyword.iskeyword(str_val) and
#            re.match("[_A-Za-z][_a-zA-Z0-9]*$", str_val) is not None)


class RecordMeta(type):
    def __new__(mcs, name, bases, dct):
        if len(bases) != 1:
            raise TypeError("Inheriting from multiple bases is not supported")
        init = dct.get('__init__')
        all_keys = [] if bases[0] is object else list(bases[0]._keys)
        if init:
            argspec = inspect.getargspec(init)
            if (argspec.varargs, argspec.keywords) != (None, None):
                raise TypeError("Varargs and keywords are not allowed")
            if '_keys' in argspec.args or '_frozen' in argspec.args:
                raise TypeError("No cheating")

            for k in argspec.args[1:]:
                all_keys.append(k) if k not in all_keys else ''

            # Override __init__ to freeze instance immediately after
            # user-defined __init__ has exited. If user's class doesn't have
            # __init__, some superclass' __init__ will take care of freezing.
            # Instance is conidered to be frozen when it has _frozen property
            # with value 1. Since superclass might also have wrapped init that
            # freezes on exit, in order to support calling superclass' __init__
            # within child class __init__ and still be able to set values,
            # add 1/subtract 1 logic makes sure that _frozen has value 1 only
            # when outermost (child class') __init__ exits.
            def wrapped_init(self, *args, **kwargs):
                if not hasattr(self, '_frozen'):
                    self._frozen = 2
                else:
                    self._frozen += 1
                init(self, *args, **kwargs)  # call user-defined __init__
                self._frozen -= 1
                if self._frozen == 1:  # last __init__ has exited, check values
                    assigned_keys = self.__dict__.keys()
                    assigned_keys.remove('_frozen')
                    if sorted(all_keys) != sorted(assigned_keys):
                        raise TypeError("Must assign only and all fields "
                                        "specified by __init__ parameters")
                    # it is ok to pass unhashable values to __init__, but user
                    # must take care to convert them to hashable. after
                    # outermost __init__ exits, all fields must be hashable
                    for v in self.__dict__.values():
                        hash(v)


            dct['__init__'] = wrapped_init
            dct['_keys'] = tuple(all_keys)
        return type.__new__(mcs, name, bases, dct)


class Record(object):
    __metaclass__ = RecordMeta

    def __setattr__(self, name, value):
        if hasattr(self, '_frozen') and self._frozen == 1:
            raise TypeError('{0} is immutable'.format(self.__class__.__name__))
        self.__dict__[name] = value

    def __init__(self):
        pass  # safeguard to assure metaclass has something to wrap

    def _replace(self, **kwargs):
        if '_frozen' in kwargs.keys():
            raise TypeError("Nope")
        if any(k not in self._keys for k in kwargs.keys()):
            raise TypeError("Invalid parameter name, only field names allowed")
        dup = copy(self)
        dup.__dict__.update(kwargs)
        return dup

    def __eq__(self, other):
        if isinstance(other, tuple):
            return tuple(getattr(self, k) for k in self._keys) == other
        elif type(other) == type(self):
            return all(getattr(self, k) == getattr(other, k)
                       for k in self._keys)
        return False

    def __repr__(self):
        keyvals = ['{0}={1}'.format(k, getattr(self, k)) for k in self._keys]
        return '{0}({1})'.format(self.__class__.__name__, ', '.join(keyvals))

    def __hash__(self):
        vals = tuple(getattr(self, k) for k in self._keys)
        # prevent records of different types with same fields from having same
        # hashes by including class itself along with values
        return hash((self.__class__,) + vals)
